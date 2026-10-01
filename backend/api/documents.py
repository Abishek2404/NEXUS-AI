from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import tempfile

from backend.services.pdf_service import extract_text_from_pdf
from backend.services.chunk_service import create_chunks
from backend.services.embedding_service import generate_embeddings
from backend.services.vector_service import store_chunks


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    """
    Complete document processing pipeline:

    PDF
      ↓
    Validate
      ↓
    Extract text
      ↓
    Create chunks
      ↓
    Generate embeddings
      ↓
    Store vectors in ChromaDB
      ↓
    Return document information
    """

    # ========================================================
    # VALIDATE FILE
    # ========================================================

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty."
        )

    temp_path = None

    try:

        # ====================================================
        # SAVE TEMPORARY PDF
        # ====================================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(file_bytes)
            temp_path = temp_file.name

        # ====================================================
        # EXTRACT PDF TEXT
        # ====================================================

        pdf_data = extract_text_from_pdf(
            temp_path
        )

        pages = pdf_data.get(
            "pages",
            []
        )

        # ====================================================
        # CREATE CHUNKS
        # ====================================================

        chunks = create_chunks(
            pages=pages,
            file_name=file.filename
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No readable text was found "
                    "in the PDF."
                )
            )

        # ====================================================
        # GENERATE EMBEDDINGS
        # ====================================================

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = generate_embeddings(
            texts
        )

        # ====================================================
        # STORE IN CHROMADB
        # ====================================================

        stored_chunks = store_chunks(
            chunks=chunks,
            embeddings=embeddings
        )

        # ====================================================
        # RETURN RESULT
        # ====================================================

        return {
            "success": True,
            "file_name": file.filename,

            "total_pages": pdf_data.get(
                "total_pages",
                0
            ),

            "total_characters": pdf_data.get(
                "total_characters",
                0
            ),

            "total_chunks": len(chunks),

            "stored_chunks": stored_chunks
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"PDF processing failed: {str(error)}"
            )
        )

    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)