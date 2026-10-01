def evaluate_quiz(
    questions: list[dict],
    answers: list[str]
) -> dict:

    if len(questions) != len(answers):
        raise ValueError(
            "Number of answers must match number of questions."
        )

    correct = 0
    question_results = []

    difficulty_stats = {
        "Easy": {
            "correct": 0,
            "total": 0
        },
        "Medium": {
            "correct": 0,
            "total": 0
        },
        "Hard": {
            "correct": 0,
            "total": 0
        }
    }

    for index, question in enumerate(questions):

        user_answer = answers[index]

        correct_answer = question.get(
            "correct_answer",
            ""
        )

        is_correct = (
            user_answer == correct_answer
        )

        if is_correct:
            correct += 1

        difficulty = question.get(
            "difficulty",
            "Medium"
        )

        if difficulty not in difficulty_stats:
            difficulty = "Medium"

        difficulty_stats[difficulty]["total"] += 1

        if is_correct:
            difficulty_stats[difficulty]["correct"] += 1

        question_results.append({
            "question_number": index + 1,
            "question": question.get(
                "question",
                ""
            ),
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "difficulty": difficulty,
            "explanation": question.get(
                "explanation",
                ""
            )
        })

    total = len(questions)

    percentage = (
        correct / total * 100
        if total > 0
        else 0
    )

    weak_areas = []

    for difficulty, stats in difficulty_stats.items():

        if stats["total"] == 0:
            continue

        difficulty_percentage = (
            stats["correct"]
            / stats["total"]
            * 100
        )

        if difficulty_percentage < 60:
            weak_areas.append({
                "area": f"{difficulty} questions",
                "score": round(
                    difficulty_percentage,
                    2
                )
            })

    if percentage < 50:

        recommendation = (
            "You need to revise this topic "
            "before attempting another quiz."
        )

    elif percentage < 80:

        recommendation = (
            "You have a basic understanding. "
            "Review the incorrect questions "
            "and practice this topic again."
        )

    else:

        recommendation = (
            "You have a strong understanding "
            "of this topic. Try a harder quiz."
        )

    return {
        "correct": correct,
        "total": total,
        "percentage": round(
            percentage,
            2
        ),
        "difficulty_analysis": difficulty_stats,
        "weak_areas": weak_areas,
        "recommendation": recommendation,
        "question_results": question_results
    }