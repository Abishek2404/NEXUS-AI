import json
import re
import time

from google import genai

from backend.config import GEMINI_API_KEY, GEMINI_MODEL


client = genai.Client(
    api_key=GEMINI_API_KEY
)


PRIMARY_MODEL = GEMINI_MODEL
FALLBACK_MODEL = "gemini-2.5-flash-lite"

MAX_RETRIES = 3


def extract_json(text: str) -> str:
    """
    Extract JSON from Gemini response.
    Handles markdown code fences and extra text.
    """

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "Could not find valid JSON in AI response."
        )

    return text[start:end + 1]


def generate_with_retry(prompt: str) -> str:

    models = [
        PRIMARY_MODEL,
        FALLBACK_MODEL
    ]

    last_error = None

    for model in models:

        for attempt in range(MAX_RETRIES):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                response_text = response.text or ""

                if not response_text.strip():
                    raise ValueError(
                        "Gemini returned an empty response."
                    )

                return response_text

            except Exception as error:

                last_error = error

                error_text = str(error).upper()

                transient_error = any(
                    value in error_text
                    for value in [
                        "503",
                        "UNAVAILABLE",
                        "429",
                        "RESOURCE_EXHAUSTED",
                        "HIGH DEMAND"
                    ]
                )

                if not transient_error:
                    raise

                if attempt < MAX_RETRIES - 1:

                    wait_time = 2 ** attempt

                    time.sleep(wait_time)

    raise RuntimeError(
        f"Learning plan generation failed: {last_error}"
    )


def generate_learning_plan(
    topic: str,
    quiz_result: dict
) -> dict:

    if not topic or not topic.strip():
        raise ValueError(
            "Topic cannot be empty."
        )

    if not isinstance(quiz_result, dict):
        raise ValueError(
            "quiz_result must be an object."
        )

    score = float(
        quiz_result.get(
            "percentage",
            0
        )
    )

    weak_areas = quiz_result.get(
        "weak_areas",
        []
    )

    difficulty_analysis = quiz_result.get(
        "difficulty_analysis",
        {}
    )

    question_results = quiz_result.get(
        "question_results",
        []
    )

    prompt = f"""
You are NEXUS AI, an adaptive AI study mentor.

Create a personalized learning plan based ONLY
on the student's quiz performance.

Topic:
{topic}

Score:
{score}%

Weak Areas:
{json.dumps(weak_areas, ensure_ascii=False)}

Difficulty Analysis:
{json.dumps(difficulty_analysis, ensure_ascii=False)}

Question Results:
{json.dumps(question_results, ensure_ascii=False)}

Create a practical study roadmap.

Return ONLY valid JSON.

Required format:

{{
    "topic": "{topic}",
    "score": {score},
    "status": "Needs Improvement",
    "recommended_study_days": 5,
    "focus": "Short description of what the student should focus on.",
    "weak_areas": [
        "Weak area 1",
        "Weak area 2"
    ],
    "plan": [
        {{
            "day": 1,
            "activity": "Review",
            "description": "What the student should study."
        }}
    ]
}}

Rules:

1. Use the quiz performance to personalize the plan.
2. Do not invent weaknesses that are not supported by the quiz data.
3. Keep the plan practical.
4. Recommended study days must be between 3 and 7.
5. Create one plan entry for each study day.
6. Keep descriptions concise.
7. Return JSON only.
"""

    response_text = generate_with_retry(
        prompt
    )

    json_text = extract_json(
        response_text
    )

    try:

        learning_plan = json.loads(
            json_text
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid JSON returned by AI: {error}"
        )

    if not isinstance(
        learning_plan,
        dict
    ):
        raise ValueError(
            "Learning plan must be a JSON object."
        )

    learning_plan["topic"] = topic
    learning_plan["score"] = score

    if "plan" not in learning_plan:
        learning_plan["plan"] = []

    if not isinstance(
        learning_plan["plan"],
        list
    ):
        raise ValueError(
            "Learning plan 'plan' must be a list."
        )

    return learning_plan