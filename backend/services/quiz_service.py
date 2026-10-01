import json
import re
import time

from google import genai

from backend.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)

from backend.services.rag_service import (
    retrieve_relevant_chunks
)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# QUIZ MODEL CONFIGURATION
# ============================================================

# Primary model comes from backend.config
PRIMARY_MODEL = GEMINI_MODEL

# Lightweight fallback model
FALLBACK_MODEL = "gemini-2.5-flash-lite"

MAX_RETRIES = 3


# ============================================================
# EXTRACT JSON
# ============================================================

def extract_json(text: str) -> str:
    """
    Extract JSON from a model response that may contain
    markdown code fences or additional text.
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


# ============================================================
# GEMINI GENERATION WITH RETRY
# ============================================================

def generate_quiz_response(
    prompt: str
):
    """
    Generate quiz content with retry handling.

    503 errors are temporary service availability errors,
    so retry using exponential backoff.

    After retries fail, use the lightweight fallback model.
    """

    last_error = None

    # --------------------------------------------------------
    # PRIMARY MODEL
    # --------------------------------------------------------

    for attempt in range(
        MAX_RETRIES
    ):

        try:

            response = client.models.generate_content(
                model=PRIMARY_MODEL,
                contents=prompt
            )

            return response

        except Exception as error:

            last_error = error

            error_text = str(error)

            # Retry only likely transient errors
            is_transient = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "high demand" in error_text.lower()
            )

            if not is_transient:
                raise

            # Don't sleep after the final attempt
            if attempt == MAX_RETRIES - 1:
                break

            delay = 2 ** attempt

            print(
                f"Quiz model temporarily unavailable. "
                f"Retrying in {delay} seconds..."
            )

            time.sleep(delay)

    # --------------------------------------------------------
    # FALLBACK MODEL
    # --------------------------------------------------------

    print(
        "Primary quiz model unavailable. "
        f"Trying fallback model: {FALLBACK_MODEL}"
    )

    try:

        response = client.models.generate_content(
            model=FALLBACK_MODEL,
            contents=prompt
        )

        return response

    except Exception as fallback_error:

        raise RuntimeError(
            "Quiz generation service is temporarily "
            "unavailable. Please try again shortly. "
            f"Primary error: {last_error}. "
            f"Fallback error: {fallback_error}"
        ) from fallback_error


# ============================================================
# GENERATE QUIZ
# ============================================================

def generate_quiz(
    topic: str,
    number_of_questions: int = 5
) -> dict:

    # --------------------------------------------------------
    # VALIDATE NUMBER OF QUESTIONS
    # --------------------------------------------------------

    if number_of_questions < 1:

        raise ValueError(
            "number_of_questions must be at least 1."
        )

    if number_of_questions > 10:

        raise ValueError(
            "Maximum 10 questions allowed."
        )

    # --------------------------------------------------------
    # VALIDATE TOPIC
    # --------------------------------------------------------

    if not topic or not topic.strip():

        raise ValueError(
            "Quiz topic cannot be empty."
        )

    topic = topic.strip()

    # --------------------------------------------------------
    # RETRIEVE COURSE MATERIAL
    # --------------------------------------------------------

    chunks = retrieve_relevant_chunks(
        topic,
        top_k=6
    )

    if not chunks:

        raise ValueError(
            "No relevant course material found."
        )

    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    context_parts = []

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        chunk_text = chunk.get(
            "text",
            ""
        )

        context_parts.append(
            f"""
SOURCE {index}

{chunk_text}
"""
        )

    context = "\n".join(
        context_parts
    )

    # --------------------------------------------------------
    # QUIZ PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are NEXUS AI, an AI study mentor.

Create a multiple-choice quiz using ONLY
the study material provided below.

Topic:
{topic}

Number of questions:
{number_of_questions}

Difficulty distribution:
- 40% Easy
- 40% Medium
- 20% Hard

Every question must have exactly four options.

Return ONLY valid JSON.

Required JSON format:

{{
    "topic": "{topic}",
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "correct_answer": "Option A",
            "difficulty": "Easy",
            "explanation": "Short explanation"
        }}
    ]
}}

Rules:

1. Every question must be answerable from
   the study material.

2. Do not invent information.

3. Do not use outside knowledge.

4. Do not duplicate questions.

5. correct_answer must exactly match
   one of the four options.

6. Keep explanations concise.

7. Return exactly {number_of_questions}
   questions.

8. Return JSON only.

STUDY MATERIAL:

{context}
"""

    # --------------------------------------------------------
    # GENERATE RESPONSE
    # --------------------------------------------------------

    response = generate_quiz_response(
        prompt
    )

    response_text = (
        response.text
        or ""
    )

    if not response_text.strip():

        raise ValueError(
            "Gemini returned an empty response."
        )

    # --------------------------------------------------------
    # EXTRACT JSON
    # --------------------------------------------------------

    json_text = extract_json(
        response_text
    )

    try:

        quiz = json.loads(
            json_text
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "AI returned invalid JSON."
        ) from error

    # --------------------------------------------------------
    # VALIDATE QUIZ STRUCTURE
    # --------------------------------------------------------

    if "questions" not in quiz:

        raise ValueError(
            "AI response does not contain questions."
        )

    questions = quiz["questions"]

    if not isinstance(
        questions,
        list
    ):

        raise ValueError(
            "AI questions must be a list."
        )

    if len(questions) != number_of_questions:

        raise ValueError(
            "AI returned an incorrect number "
            "of questions."
        )

    # --------------------------------------------------------
    # VALIDATE EACH QUESTION
    # --------------------------------------------------------

    for index, question in enumerate(
        questions,
        start=1
    ):

        if not isinstance(
            question,
            dict
        ):

            raise ValueError(
                f"Question {index} is invalid."
            )

        required_fields = [
            "question",
            "options",
            "correct_answer",
            "difficulty",
            "explanation"
        ]

        for field in required_fields:

            if field not in question:

                raise ValueError(
                    f"Question {index} is missing "
                    f"'{field}'."
                )

        options = question["options"]

        if not isinstance(
            options,
            list
        ):

            raise ValueError(
                f"Question {index} options "
                "must be a list."
            )

        if len(options) != 4:

            raise ValueError(
                f"Question {index} must have "
                "exactly four options."
            )

        correct_answer = question[
            "correct_answer"
        ]

        if correct_answer not in options:

            raise ValueError(
                f"Question {index} has a "
                "correct_answer that does not "
                "match any option."
            )

    # --------------------------------------------------------
    # NORMALIZE TOPIC
    # --------------------------------------------------------

    quiz["topic"] = topic

    return quiz