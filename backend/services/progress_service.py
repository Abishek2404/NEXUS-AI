import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


# ============================================================
# STORAGE LOCATION
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
DATA_FILE = DATA_DIR / "progress.json"


# ============================================================
# INITIALIZE STORAGE
# ============================================================

def initialize_database():
    """
    Create the progress storage directory/file
    if they do not already exist.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not DATA_FILE.exists():

        DATA_FILE.write_text(
            "{}",
            encoding="utf-8"
        )


# ============================================================
# LOAD DATA
# ============================================================

def load_progress() -> Dict[str, Any]:

    initialize_database()

    try:

        content = DATA_FILE.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            return {}

        data = json.loads(content)

        if isinstance(data, dict):
            return data

        return {}

    except (
        json.JSONDecodeError,
        OSError
    ):

        return {}


# ============================================================
# SAVE DATA
# ============================================================

def save_progress(
    data: Dict[str, Any]
):

    initialize_database()

    temp_file = DATA_FILE.with_suffix(
        ".tmp"
    )

    temp_file.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    temp_file.replace(
        DATA_FILE
    )


# ============================================================
# SAVE QUIZ ATTEMPT
# ============================================================

def save_quiz_attempt(
    student_id: str,
    topic: str,
    score: float,
    correct: int,
    total: int
) -> Dict[str, Any]:

    student_id = student_id.strip()
    topic = topic.strip()

    if not student_id:

        raise ValueError(
            "student_id cannot be empty."
        )

    if not topic:

        raise ValueError(
            "topic cannot be empty."
        )

    if total < 1:

        raise ValueError(
            "total must be at least 1."
        )

    if correct < 0 or correct > total:

        raise ValueError(
            "correct must be between 0 and total."
        )

    score = max(
        0.0,
        min(
            float(score),
            100.0
        )
    )

    data = load_progress()

    if student_id not in data:

        data[student_id] = {
            "attempts": []
        }

    if not isinstance(
        data[student_id],
        dict
    ):

        data[student_id] = {
            "attempts": []
        }

    if "attempts" not in data[student_id]:

        data[student_id]["attempts"] = []

    attempt = {

        "topic": topic,

        "score": score,

        "correct": correct,

        "total": total,

        "created_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    data[student_id]["attempts"].append(
        attempt
    )

    save_progress(data)

    return attempt


# ============================================================
# GET STUDENT PROGRESS
# ============================================================

def get_student_progress(
    student_id: str
) -> Dict[str, Any]:

    student_id = student_id.strip()

    if not student_id:

        raise ValueError(
            "student_id cannot be empty."
        )

    data = load_progress()

    student_data = data.get(
        student_id,
        {}
    )

    attempts: List[Dict[str, Any]] = (
        student_data.get(
            "attempts",
            []
        )
    )

    if not attempts:

        return {

            "student_id": student_id,

            "overall": {

                "total_attempts": 0,

                "average_score": 0,

                "best_score": 0
            },

            "topics": [],

            "attempts": []
        }

    # --------------------------------------------------------
    # OVERALL STATISTICS
    # --------------------------------------------------------

    scores = [

        float(
            attempt.get(
                "score",
                0
            )
        )

        for attempt in attempts
    ]

    average_score = (
        sum(scores) / len(scores)
    )

    best_score = max(scores)

    overall = {

        "total_attempts": len(attempts),

        "average_score": average_score,

        "best_score": best_score
    }

    # --------------------------------------------------------
    # TOPIC STATISTICS
    # --------------------------------------------------------

    topic_groups: Dict[
        str,
        List[float]
    ] = {}

    for attempt in attempts:

        topic = attempt.get(
            "topic",
            "Unknown"
        )

        score = float(
            attempt.get(
                "score",
                0
            )
        )

        if topic not in topic_groups:

            topic_groups[topic] = []

        topic_groups[topic].append(
            score
        )

    topics = []

    for topic, topic_scores in topic_groups.items():

        topics.append({

            "topic": topic,

            "average_score": (
                sum(topic_scores)
                / len(topic_scores)
            ),

            "attempts": len(
                topic_scores
            ),

            "best_score": max(
                topic_scores
            )
        })

    # --------------------------------------------------------
    # SORT HISTORY
    # --------------------------------------------------------

    attempts_sorted = sorted(
        attempts,
        key=lambda item: item.get(
            "created_at",
            ""
        ),
        reverse=True
    )

    return {

        "student_id": student_id,

        "overall": overall,

        "topics": topics,

        "attempts": attempts_sorted
    }