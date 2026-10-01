from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.quiz_service import generate_quiz


router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)


class QuizRequest(BaseModel):

    topic: str = Field(
        min_length=2,
        max_length=200
    )

    number_of_questions: int = Field(
        default=5,
        ge=1,
        le=10
    )


@router.post("/generate")
def create_quiz(request: QuizRequest):

    try:

        quiz = generate_quiz(
            topic=request.topic,
            number_of_questions=request.number_of_questions
        )

        return quiz

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Quiz generation error: {str(error)}"
        )