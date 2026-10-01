from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.rag_service import (
    answer_question
)


router = APIRouter(
    prefix="/tutor",
    tags=["AI Tutor"]
)


class TutorRequest(BaseModel):

    question: str


@router.post("/ask")
async def ask_tutor(
    request: TutorRequest
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = answer_question(
            request.question
        )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"AI Tutor failed: {str(error)}"
            )
        )