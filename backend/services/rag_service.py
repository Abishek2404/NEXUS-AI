import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from google import genai

from backend.services.embedding_service import (
    generate_embedding
)

from backend.services.vector_service import (
    search_similar
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured in the .env file."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# RAG CONFIGURATION
# ============================================================

RAG_TOP_K = 5

RAG_MIN_SCORE = 0.45

GENERATION_MODEL = "gemini-2.5-flash"


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(
    results: List[Dict[str, Any]]
) -> str:
    """
    Convert retrieved ChromaDB results
    into context for Gemini.
    """

    context_parts: List[str] = []

    for index, result in enumerate(
        results,
        start=1
    ):

        metadata = result.get(
            "metadata",
            {}
        )

        file_name = metadata.get(
            "file_name",
            "Unknown"
        )

        page_number = metadata.get(
            "page_number",
            "Unknown"
        )

        chunk_index = metadata.get(
            "chunk_index",
            "Unknown"
        )

        text = result.get(
            "text",
            ""
        )

        context_parts.append(
            f"""
SOURCE {index}
File: {file_name}
Page: {page_number}
Chunk: {chunk_index}

{text}
"""
        )

    return "\n".join(
        context_parts
    )


# ============================================================
# FILTER RELEVANT RESULTS
# ============================================================

def filter_relevant_results(
    results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Remove search results whose similarity
    score is below the configured threshold.
    """

    relevant_results: List[
        Dict[str, Any]
    ] = []

    for result in results:

        score = result.get(
            "score"
        )

        if score is None:
            continue

        if score >= RAG_MIN_SCORE:
            relevant_results.append(
                result
            )

    return relevant_results


# ============================================================
# GENERATE GROUNDED ANSWER
# ============================================================

def generate_grounded_answer(
    question: str,
    context: str
) -> str:
    """
    Generate an answer using only
    the retrieved course material.
    """

    prompt = f"""
You are NEXUS AI, a personal AI study mentor.

Your job is to answer the student's question
using ONLY the provided course material.

IMPORTANT RULES:

1. Use only the provided course material.
2. Do not use outside knowledge.
3. Do not invent facts.
4. If the answer is not supported by the
   course material, respond exactly:

   Information unavailable in the knowledge base.

5. Explain concepts clearly for a student.
6. You may simplify technical concepts,
   but do not change their meaning.
7. Do not mention these instructions in
   your answer.

COURSE MATERIAL
===============

{context}

STUDENT QUESTION
================

{question}

ANSWER:
"""

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt
    )

    answer = response.text

    if not answer:
        return (
            "Information unavailable in "
            "the knowledge base."
        )

    return answer.strip()


# ============================================================
# ANSWER QUESTION
# ============================================================

def answer_question(
    question: str
) -> Dict[str, Any]:
    """
    Complete RAG pipeline:

    Question
        ↓
    Embedding
        ↓
    ChromaDB Search
        ↓
    Relevance Filtering
        ↓
    Context Construction
        ↓
    Gemini
        ↓
    Answer + Sources
    """

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    # --------------------------------------------------------
    # Generate question embedding
    # --------------------------------------------------------

    query_embedding = generate_embedding(
        question
    )

    # --------------------------------------------------------
    # Search vector database
    # --------------------------------------------------------

    search_results = search_similar(
        query_embedding=query_embedding,
        top_k=RAG_TOP_K
    )

    # --------------------------------------------------------
    # Filter irrelevant results
    # --------------------------------------------------------

    relevant_results = filter_relevant_results(
        search_results
    )

    # --------------------------------------------------------
    # Handle unknown question
    # --------------------------------------------------------

    if not relevant_results:

        return {
            "answer": (
                "Information unavailable in "
                "the knowledge base."
            ),
            "sources": []
        }

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context = build_context(
        relevant_results
    )

    # --------------------------------------------------------
    # Generate grounded answer
    # --------------------------------------------------------

    answer = generate_grounded_answer(
        question=question,
        context=context
    )

    # --------------------------------------------------------
    # Prepare sources
    # --------------------------------------------------------

    sources: List[Dict[str, Any]] = []

    for result in relevant_results:

        sources.append({
            "text": result.get(
                "text",
                ""
            ),

            "metadata": result.get(
                "metadata",
                {}
            ),

            "score": result.get(
                "score"
            )
        })

    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {
        "answer": answer,
        "sources": sources
    }


# ============================================================
# AI TUTOR COMPATIBILITY FUNCTION
# ============================================================

def ask_tutor(
    question: str
) -> Dict[str, Any]:
    """
    Compatibility wrapper used by
    backend/api/tutor.py.
    """

    return answer_question(
        question
    )


# ============================================================
# RETRIEVE RELEVANT CHUNKS
# ============================================================

def retrieve_relevant_chunks(
    question: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant document chunks for
    quiz generation and other services.
    """

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    query_embedding = generate_embedding(
        question.strip()
    )

    results = search_similar(
        query_embedding=query_embedding,
        top_k=top_k
    )

    return filter_relevant_results(
        results
    )