def generate_learning_plan(
    topic: str,
    quiz_result: dict
) -> dict:

    score = float(
        quiz_result.get("percentage", 0)
    )

    difficulty_analysis = quiz_result.get(
        "difficulty_analysis",
        {}
    )

    weak_areas = quiz_result.get(
        "weak_areas",
        []
    )

    question_results = quiz_result.get(
        "question_results",
        []
    )

    incorrect_questions = [
        question
        for question in question_results
        if not question.get("is_correct", False)
    ]

    # --------------------------------------------------
    # Determine learning status
    # --------------------------------------------------

    if score >= 80:

        status = "Strong"

        focus = (
            "You have a strong understanding of this topic. "
            "Focus on advanced concepts and challenging problems."
        )

        study_days = 3

    elif score >= 60:

        status = "Developing"

        focus = (
            "You have a reasonable understanding, but "
            "some concepts need additional practice."
        )

        study_days = 5

    else:

        status = "Needs Revision"

        focus = (
            "Your fundamentals need strengthening before "
            "moving to more advanced concepts."
        )

        study_days = 7

    # --------------------------------------------------
    # Build learning activities
    # --------------------------------------------------

    plan = []

    if score < 60:

        plan.append(
            {
                "day": 1,
                "activity": "Review fundamentals",
                "description": (
                    f"Review the core concepts of {topic} "
                    "using your uploaded study material."
                )
            }
        )

        plan.append(
            {
                "day": 2,
                "activity": "Review incorrect concepts",
                "description": (
                    "Go through every question you answered "
                    "incorrectly and understand why the correct "
                    "answer is correct."
                )
            }
        )

        plan.append(
            {
                "day": 3,
                "activity": "Practice basic questions",
                "description": (
                    "Complete 10 easy questions related to "
                    f"{topic}."
                )
            }

        )

        plan.append(
            {
                "day": 4,
                "activity": "Practice medium questions",
                "description": (
                    "Complete 10 medium-level questions and "
                    "review every incorrect answer."
                )
            }
        )

        plan.append(
            {
                "day": 5,
                "activity": "Target weak areas",
                "description": (
                    "Spend focused study time on the areas "
                    "where your quiz performance was lowest."
                )
            }
        )

        plan.append(
            {
                "day": 6,
                "activity": "Mixed practice",
                "description": (
                    "Complete a mixed set of easy, medium "
                    "and hard questions."
                )
            }
        )

        plan.append(
            {
                "day": 7,
                "activity": "Retake assessment",
                "description": (
                    "Take another assessment on this topic "
                    "and compare your performance."
                )
            }
        )

    elif score < 80:

        plan.append(
            {
                "day": 1,
                "activity": "Review mistakes",
                "description": (
                    "Review the questions you answered "
                    "incorrectly."
                )
            }
        )

        plan.append(
            {
                "day": 2,
                "activity": "Focused practice",
                "description": (
                    f"Practice questions specifically related "
                    f"to {topic}."
                )
            }
        )

        plan.append(
            {
                "day": 3,
                "activity": "Medium-level practice",
                "description": (
                    "Complete a medium-difficulty practice set."
                )
            }
        )

        plan.append(
            {
                "day": 4,
                "activity": "Weak-area revision",
                "description": (
                    "Review the concepts responsible for "
                    "your incorrect answers."
                )
            }
        )

        plan.append(
            {
                "day": 5,
                "activity": "Retake assessment",
                "description": (
                    "Take another quiz and compare your "
                    "new score with the previous attempt."
                )
            }
        )

    else:

        plan.append(
            {
                "day": 1,
                "activity": "Advanced concepts",
                "description": (
                    f"Explore advanced concepts related to "
                    f"{topic}."
                )
            }
        )

        plan.append(
            {
                "day": 2,
                "activity": "Hard practice",
                "description": (
                    "Complete challenging questions to "
                    "test deeper understanding."
                )
            }
        )

        plan.append(
            {
                "day": 3,
                "activity": "Challenge assessment",
                "description": (
                    "Take a harder assessment and attempt "
                    "to improve your score."
                )
            }
        )

    # --------------------------------------------------
    # Weak area summary
    # --------------------------------------------------

    weak_area_names = [
        area.get("area", "Unknown")
        for area in weak_areas
    ]

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    return {
        "topic": topic,
        "score": score,
        "status": status,
        "focus": focus,
        "recommended_study_days": study_days,
        "weak_areas": weak_area_names,
        "incorrect_question_count": len(
            incorrect_questions
        ),
        "plan": plan
    }