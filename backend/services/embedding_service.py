import os
from typing import List

from dotenv import load_dotenv
from google import genai


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured in the .env file."
    )


client = genai.Client(
    api_key=GOOGLE_API_KEY
)


EMBEDDING_MODEL = "gemini-embedding-001"


# ============================================================
# GENERATE SINGLE EMBEDDING
# ============================================================
def generate_embedding(text: str) -> List[float]:
    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty."
        )

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    if not response.embeddings:
        raise ValueError(
            "No embedding returned from Google."
        )

    values = response.embeddings[0].values

    if values is None:
        raise ValueError(
            "Embedding values are empty."
        )

    return list(values)
# ============================================================
# GENERATE MULTIPLE EMBEDDINGS
# ============================================================

def generate_embeddings(
    texts: List[str]
) -> List[List[float]]:
    """
    Generate embeddings for multiple text chunks.
    """

    if not texts:
        return []

    embeddings = []

    for text in texts:

        embedding = generate_embedding(
            text
        )

        embeddings.append(
            embedding
        )

    return embeddings