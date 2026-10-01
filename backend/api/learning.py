from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from backend.services.learning_service import (
    generate_learning_plan
)


router = APIRouter(
    prefix="/learning",
    tags=["Learning"]
)


class LearningPlanRequest(BaseModel):

    topic: str

    quiz_result: Dict[str, Any]


@router.post("/plan")
async def create_learning_plan(
    request: LearningPlanRequest
):

    try:

        result = generate_learning_plan(
            topic=request.topic,
            quiz_result=request.quiz_result
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Learning plan generation error: {error}"
        )