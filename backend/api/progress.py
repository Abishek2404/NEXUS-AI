from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.progress_service import (
    save_quiz_attempt,
    get_student_progress
)


router = APIRouter(
    prefix="/progress",
    tags=["Progress"]
)


class ProgressAttemptRequest(BaseModel):

    student_id: str = Field(
        min_length=1
    )

    topic: str = Field(
        min_length=1
    )

    score: float = Field(
        ge=0,
        le=100
    )

    correct: int = Field(
        ge=0
    )

    total: int = Field(
        ge=1
    )


@router.post("/attempt")
async def create_progress_attempt(
    request: ProgressAttemptRequest
):

    if request.correct > request.total:

        raise HTTPException(
            status_code=400,
            detail=(
                "correct cannot be greater "
                "than total."
            )
        )

    try:

        attempt = save_quiz_attempt(
            student_id=request.student_id,
            topic=request.topic,
            score=request.score,
            correct=request.correct,
            total=request.total
        )

        return {
            "success": True,
            "message": "Quiz attempt saved.",
            "attempt": attempt
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not save progress: {error}"
            )
        )


@router.get("/{student_id}")
async def get_progress(
    student_id: str
):

    try:

        return get_student_progress(
            student_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not load progress: {error}"
            )
        )