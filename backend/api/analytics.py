from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.analytics_service import evaluate_quiz


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


class QuizEvaluationRequest(BaseModel):
    questions: list[dict]
    answers: list[str]


@router.post("/evaluate")
def evaluate_quiz_api(
    request: QuizEvaluationRequest
):
    try:
        return evaluate_quiz(
            questions=request.questions,
            answers=request.answers
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation error: {str(error)}"
        )