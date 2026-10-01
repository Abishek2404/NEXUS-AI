from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.rag_service import ask_tutor


router = APIRouter(
    prefix="/tutor",
    tags=["AI Tutor"]
)


class TutorRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_ai_tutor(request: TutorRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = ask_tutor(question)

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"AI Tutor error: {str(error)}"
        )