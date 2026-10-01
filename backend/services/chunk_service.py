from typing import List, Dict


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """

    if not text:
        return ""

    # Remove excessive whitespace
    text = " ".join(text.split())

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Split text into overlapping chunks.
    """

    text = clean_text(text)

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be smaller than chunk size."
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def create_chunks(
    pages: List[Dict],
    file_name: str = ""
) -> List[Dict]:
    """
    Create chunks while preserving page metadata.
    """

    all_chunks = []

    chunk_index = 0

    for page in pages:

        page_number = page.get(
            "page_number",
            0
        )

        page_text = page.get(
            "text",
            ""
        )

        chunks = chunk_text(page_text)

        for chunk in chunks:

            all_chunks.append(
                {
                    "text": chunk,
                    "metadata": {
                        "file_name": file_name,
                        "page_number": page_number,
                        "chunk_index": chunk_index
                    }
                }
            )

            chunk_index += 1

    return all_chunks