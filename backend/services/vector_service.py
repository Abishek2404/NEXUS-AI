import os
from typing import Any, Dict, List

import chromadb


# ============================================================
# CHROMADB CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "chroma"
)

COLLECTION_NAME = "nexus_documents"


# ============================================================
# CHROMADB CLIENT
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "hnsw:space": "cosine"
    }
)


# ============================================================
# STORE CHUNKS
# ============================================================

def store_chunks(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]]
) -> int:

    if not chunks:
        return 0

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks and embeddings must match."
        )

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for index, chunk in enumerate(chunks):

        metadata = chunk.get(
            "metadata",
            {}
        )

        file_name = metadata.get(
            "file_name",
            "unknown"
        )

        page_number = metadata.get(
            "page_number",
            0
        )

        chunk_index = metadata.get(
            "chunk_index",
            index
        )

        chunk_id = (
            f"{file_name}"
            f"_page_{page_number}"
            f"_chunk_{chunk_index}"
        )

        ids.append(chunk_id)

        documents.append(
            str(chunk.get("text", ""))
        )

        metadatas.append({
            "file_name": str(file_name),
            "page_number": int(page_number),
            "chunk_index": int(chunk_index)
        })

    # ChromaDB's type definitions can be stricter
    # than the actual runtime API.
    collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings, # type: ignore[arg-type]
    metadatas=metadatas,  # type: ignore[arg-type]
)
    return len(ids)


# ============================================================
# SEARCH SIMILAR CHUNKS
# ============================================================

def search_similar(
    query_embedding: List[float],
    top_k: int = 5
) -> List[Dict[str, Any]]:

    if not query_embedding:
        raise ValueError(
            "Query embedding cannot be empty."
        )

    total_documents = collection.count()

    if total_documents == 0:
        return []

    results: Any = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(
            top_k,
            total_documents
        )
    )

    if not results:
        return []

    documents = results.get(
        "documents"
    ) or [[]]

    metadatas = results.get(
        "metadatas"
    ) or [[]]

    distances = results.get(
        "distances"
    ) or [[]]

    ids = results.get(
        "ids"
    ) or [[]]

    documents = documents[0]
    metadatas = metadatas[0]
    distances = distances[0]
    ids = ids[0]

    retrieved_items: List[Dict[str, Any]] = []

    for index, document in enumerate(documents):

        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        vector_id = (
            ids[index]
            if index < len(ids)
            else None
        )

        # Chroma cosine distance:
        # 0 = identical
        # higher = less similar
        score = (
            1 - distance
            if distance is not None
            else None
        )

        retrieved_items.append({
            "vector_id": vector_id,
            "text": document,
            "metadata": metadata,
            "score": score
        })

    return retrieved_items


# ============================================================
# COLLECTION INFORMATION
# ============================================================

def get_collection_count() -> int:

    return collection.count()


# ============================================================
# CLEAR COLLECTION
# ============================================================

def clear_collection() -> None:

    global collection

    chroma_client.delete_collection(
        name=COLLECTION_NAME
    )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        }
    )