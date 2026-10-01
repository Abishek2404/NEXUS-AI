import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NEXUS AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "document_processed" not in st.session_state:
    st.session_state.document_processed = False

if "document_info" not in st.session_state:
    st.session_state.document_info = None

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

if "learning_plan" not in st.session_state:
    st.session_state.learning_plan = None

if "progress_saved" not in st.session_state:
    st.session_state.progress_saved = False

STUDENT_ID = "demo_student"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-top: 0;
    }

    .feature-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        background-color: #ffffff;
        margin-bottom: 15px;
    }

    .status-card {
        padding: 15px;
        border-radius: 12px;
        background-color: #f5f7fa;
        border: 1px solid #e1e5ea;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🧠 NEXUS AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your Personal AI Study Mentor'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🧠 NEXUS AI")

    st.write(
        "AI-powered adaptive learning platform."
    )

    st.divider()

    st.subheader("📌 System Status")

    if st.session_state.document_processed:

        st.success(
            "Knowledge Base Ready"
        )

    else:

        st.warning(
            "No course material loaded"
        )

    st.divider()

    st.caption(
        "NEXUS AI v1.0"
    )


# ============================================================
# DASHBOARD METRICS
# ============================================================

if st.session_state.document_info:

    document_info = (
        st.session_state.document_info
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📄 Pages",
            document_info["total_pages"]
        )

    with col2:
        st.metric(
            "📝 Characters",
            document_info["total_characters"]
        )

    with col3:
        st.metric(
            "🧩 Chunks",
            document_info["total_chunks"]
        )

    with col4:
        st.metric(
            "🧠 Stored",
            document_info["stored_chunks"]
        )

    st.divider()


# ============================================================
# PDF UPLOAD
# ============================================================

st.header("📚 Course Material")

st.write(
    "Upload your study material to build your personal "
    "AI knowledge base."
)

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload a text-based PDF for best results."
)


if uploaded_file is not None:

    st.info(
        f"Selected file: **{uploaded_file.name}**"
    )

    if st.button(
        "🚀 Process PDF",
        use_container_width=True
    ):

        with st.spinner(
            "Processing PDF → Chunking → Embeddings → ChromaDB..."
        ):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }

            try:

                response = requests.post(
                    f"{API_URL}/documents/upload",
                    files=files,
                    timeout=300
                )

                if response.status_code == 200:

                    data = response.json()

                    st.session_state.document_processed = True

                    st.session_state.document_info = data

                    # Clear previous quiz when a new document
                    # is uploaded.
                    st.session_state.quiz = None
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_result = None

                    st.success(
                        "PDF processed successfully! 🎉"
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Backend error: {response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to FastAPI."
                )

                st.info(
                    "Make sure the backend is running:\n\n"
                    "`uvicorn backend.main:app --reload`"
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ PDF processing timed out."
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )


# ============================================================
# AI TUTOR
# ============================================================

st.divider()

st.header("🤖 AI Tutor")

st.write(
    "Ask questions about your uploaded course material."
)

question = st.text_area(
    "Your question",
    placeholder=(
        "Example: Explain AWS EC2 in simple terms."
    ),
    height=120
)


if st.button(
    "💬 Ask NEXUS",
    use_container_width=True
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    elif not st.session_state.document_processed:

        st.warning(
            "Please upload and process a PDF first."
        )

    else:

        with st.spinner(
            "Searching your course material..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/tutor/ask",
                    json={
                        "question": question
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    tutor_data = response.json()

                    st.subheader(
                        "🧠 NEXUS Answer"
                    )

                    st.write(
                        tutor_data["answer"]
                    )

                    sources = tutor_data.get(
                        "sources",
                        []
                    )

                    if sources:

                        st.divider()

                        st.subheader(
                            "📚 Retrieved Sources"
                        )

                        for index, source in enumerate(
                            sources,
                            start=1
                        ):

                            metadata = source.get(
                                "metadata",
                                {}
                            )

                            file_name = metadata.get(
                                "file_name",
                                "Unknown"
                            )

                            chunk_index = metadata.get(
                                "chunk_index",
                                "Unknown"
                            )

                            with st.expander(
                                f"Source {index} • "
                                f"{file_name} • "
                                f"Chunk {chunk_index}"
                            ):

                                st.write(
                                    source.get(
                                        "text",
                                        ""
                                    )
                                )

                else:

                    st.error(
                        f"Tutor error: {response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to FastAPI."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ AI Tutor request timed out."
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )


# ============================================================
# AI QUIZ GENERATOR
# ============================================================

st.divider()

st.header("📝 AI Quiz Generator")

st.write(
    "Generate questions from your uploaded study material."
)

quiz_topic = st.text_input(
    "Quiz topic",
    placeholder="Example: AWS EC2"
)

number_of_questions = st.slider(
    "Number of questions",
    min_value=3,
    max_value=10,
    value=5
)


if st.button(
    "🎯 Generate Quiz",
    use_container_width=True
):

    if not st.session_state.document_processed:

        st.warning(
            "Please upload and process a PDF first."
        )

    elif not quiz_topic.strip():

        st.warning(
            "Please enter a quiz topic."
        )

    else:

        with st.spinner(
            "NEXUS is creating your quiz..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/quiz/generate",
                    json={
                        "topic": quiz_topic,
                        "number_of_questions":
                            number_of_questions
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    quiz_data = response.json()

                    st.session_state.quiz = quiz_data
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_result = None
                    st.session_state.learning_plan = None
                    st.session_state.progress_saved = False

                    st.success(
                        "Quiz generated successfully! 🎉"
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Quiz generation error: "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to FastAPI."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ Quiz generation timed out."
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )


# ============================================================
# DISPLAY QUIZ
# ============================================================

if st.session_state.quiz:

    quiz = st.session_state.quiz

    questions = quiz.get(
        "questions",
        []
    )

    st.divider()

    st.subheader(
        f"🧠 {quiz.get('topic', 'Quiz')}"
    )

    st.write(
        f"**{len(questions)} questions**"
    )

    for index, question_data in enumerate(
        questions
    ):

        st.markdown(
            f"### Question {index + 1}"
        )

        st.write(
            question_data["question"]
        )

        selected_answer = st.radio(
            "Select your answer:",
            question_data["options"],
            key=f"quiz_question_{index}"
        )

        st.session_state.quiz_answers[
            index
        ] = selected_answer

        st.caption(
            f"Difficulty: "
            f"{question_data.get('difficulty', 'Medium')}"
        )

    st.divider()

    if st.button(
        "✅ Submit Quiz",
        use_container_width=True
    ):

        answers = []

        for index in range(
            len(questions)
        ):

            answer = (
                st.session_state.quiz_answers
                .get(index, "")
            )

            answers.append(answer)

        with st.spinner(
            "Analyzing your performance..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/analytics/evaluate",
                    json={
                        "questions": questions,
                        "answers": answers
                    },
                    timeout=60
                )

                if response.status_code == 200:

                    result = response.json()

                    st.session_state.quiz_result = result
                    st.session_state.progress_saved = False

                    st.rerun()

                else:

                    st.error(
                        f"Evaluation error: "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to FastAPI."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ Evaluation timed out."
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )


# ============================================================
# QUIZ RESULT
# ============================================================

if st.session_state.quiz_result:

    result = st.session_state.quiz_result

    st.divider()

    st.header("📊 Your Performance")

    percentage = result.get(
        "percentage",
        0
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "✅ Correct",
            result.get("correct", 0)
        )

    with col2:

        st.metric(
            "📚 Total",
            result.get("total", 0)
        )

    with col3:

        st.metric(
            "🎯 Score",
            f"{percentage:.0f}%"
        )

    # --------------------------------------------------------
    # SCORE MESSAGE
    # --------------------------------------------------------

    st.subheader(
        "🎯 NEXUS Recommendation"
    )

    recommendation = result.get(
        "recommendation",
        ""
    )

    if percentage >= 80:

        st.success(
            recommendation
        )

    elif percentage >= 50:

        st.warning(
            recommendation
        )

    else:

        st.error(
            recommendation
        )

    # --------------------------------------------------------
    # WEAK AREAS
    # --------------------------------------------------------

    weak_areas = result.get(
        "weak_areas",
        []
    )

    st.subheader(
        "⚠️ Areas That Need Attention"
    )

    if weak_areas:

        for area in weak_areas:

            area_name = area.get(
                "area",
                "Unknown"
            )

            area_score = area.get(
                "score",
                0
            )

            st.warning(
                f"**{area_name}** — "
                f"{area_score:.0f}%"
            )

    else:

        st.success(
            "No major weak areas detected."
        )

    # --------------------------------------------------------
    # DIFFICULTY ANALYSIS
    # --------------------------------------------------------

    st.subheader(
        "📈 Difficulty Analysis"
    )

    difficulty_analysis = result.get(
        "difficulty_analysis",
        {}
    )

    col1, col2, col3 = st.columns(3)

    difficulty_columns = [
        (col1, "Easy"),
        (col2, "Medium"),
        (col3, "Hard")
    ]

    for column, level in difficulty_columns:

        stats = difficulty_analysis.get(
            level,
            {
                "correct": 0,
                "total": 0
            }
        )

        with column:

            st.metric(
                level,
                f"{stats.get('correct', 0)} / "
                f"{stats.get('total', 0)}"
            )

    # --------------------------------------------------------
    # QUESTION REVIEW
    # --------------------------------------------------------

    st.subheader(
        "🔍 Question Review"
    )

    question_results = result.get(
        "question_results",
        []
    )

    for question_result in question_results:

        if question_result.get(
            "is_correct",
            False
        ):

            icon = "✅"

        else:

            icon = "❌"

        question_number = question_result.get(
            "question_number",
            ""
        )

        with st.expander(
            f"{icon} Question {question_number}"
        ):

            st.write(
                question_result.get(
                    "question",
                    ""
                )
            )

            st.write(
                "**Your answer:** "
                + question_result.get(
                    "user_answer",
                    "Not answered"
                )
            )

            st.write(
                "**Correct answer:** "
                + question_result.get(
                    "correct_answer",
                    ""
                )
            )

            explanation = question_result.get(
                "explanation",
                ""
            )

            if explanation:

                st.info(
                    explanation
                )



# ============================================================
# SAVE QUIZ PROGRESS
# ============================================================

if (
    st.session_state.quiz_result
    and not st.session_state.progress_saved
):

    result = st.session_state.quiz_result
    current_quiz = st.session_state.get("quiz")

    if current_quiz:

        topic = current_quiz.get(
            "topic",
            "Unknown Topic"
        )

        try:

            progress_response = requests.post(
                f"{API_URL}/progress/attempt",
                json={
                    "student_id": STUDENT_ID,
                    "topic": topic,
                    "score": result.get(
                        "percentage",
                        0
                    ),
                    "correct": result.get(
                        "correct",
                        0
                    ),
                    "total": result.get(
                        "total",
                        0
                    )
                },
                timeout=30
            )

            if progress_response.status_code == 200:

                st.session_state.progress_saved = True

            else:

                st.warning(
                    "⚠️ Quiz result was generated, "
                    "but progress could not be saved."
                )

        except requests.exceptions.ConnectionError:

            st.warning(
                "⚠️ Could not connect to the Progress API."
            )

        except requests.exceptions.Timeout:

            st.warning(
                "⚠️ Progress saving timed out."
            )

        except Exception as error:

            st.warning(
                f"⚠️ Progress saving error: {error}"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🧠 NEXUS AI • Learn → Practice → Analyze → Improve"
)

# ============================================================
# PERSONALIZED LEARNING PLAN
# ============================================================

if st.session_state.quiz_result:

    st.divider()

    st.header("🎯 Personalized Learning Plan")

    current_quiz = st.session_state.get(
        "quiz"
    )

    quiz_result = st.session_state.get(
        "quiz_result"
    )

    if current_quiz and quiz_result:

        topic = current_quiz.get(
            "topic",
            "Current Topic"
        )

        if st.button(
            "🧠 Generate My Learning Plan",
            use_container_width=True
        ):

            with st.spinner(
                "NEXUS is analyzing your performance..."
            ):

                try:

                    response = requests.post(
                        f"{API_URL}/learning/plan",
                        json={
                            "topic": topic,
                            "quiz_result": quiz_result
                        },
                        timeout=60
                    )

                    if response.status_code == 200:

                        learning_plan = response.json()

                        st.session_state[
                            "learning_plan"
                        ] = learning_plan

                        st.rerun()

                    else:

                        st.error(
                            f"Learning plan error: "
                            f"{response.text}"
                        )

                except Exception as error:

                    st.error(
                        f"Could not generate learning plan: "
                        f"{error}"
                    )


# ============================================================
# DISPLAY LEARNING PLAN
# ============================================================

if st.session_state.get(
    "learning_plan"
):

    learning_plan = st.session_state[
        "learning_plan"
    ]

    st.divider()

    st.subheader(
        f"🗓️ {learning_plan['topic']} "
        f"Learning Roadmap"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Current Score",
            f"{learning_plan['score']:.0f}%"
        )

    with col2:

        st.metric(
            "Status",
            learning_plan["status"]
        )

    with col3:

        st.metric(
            "Study Days",
            learning_plan[
                "recommended_study_days"
            ]
        )

    st.info(
        learning_plan["focus"]
    )

    # --------------------------------------------------------
    # WEAK AREAS
    # --------------------------------------------------------

    weak_areas = learning_plan.get(
        "weak_areas",
        []
    )

    if weak_areas:

        st.subheader(
            "⚠️ Focus Areas"
        )

        for area in weak_areas:

            st.warning(
                f"Focus on: **{area}**"
            )

    # --------------------------------------------------------
    # STUDY PLAN
    # --------------------------------------------------------

    st.subheader(
        "📚 Your Study Plan"
    )

    for day in learning_plan["plan"]:

        with st.expander(
            f"Day {day['day']} — "
            f"{day['activity']}"
        ):

            st.write(
                day["description"]
            )

    st.success(
        "Follow this plan and retake the assessment "
        "after completing the recommended practice."
    )

# ============================================================
# LEARNING PROGRESS DASHBOARD
# ============================================================

st.divider()

st.header("📊 My Learning Progress")

try:

    progress_response = requests.get(
        f"{API_URL}/progress/{STUDENT_ID}",
        timeout=15
    )

    if progress_response.status_code == 200:

        progress_data = progress_response.json()

        overall = progress_data.get(
            "overall",
            {}
        )

        topics = progress_data.get(
            "topics",
            []
        )

        attempts = progress_data.get(
            "attempts",
            []
        )

        # ----------------------------------------------------
        # OVERALL METRICS
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "📝 Quiz Attempts",
                overall.get(
                    "total_attempts",
                    0
                )
            )

        with col2:

            st.metric(
                "📈 Average Score",
                f"{overall.get('average_score', 0):.1f}%"
            )

        with col3:

            st.metric(
                "🏆 Best Score",
                f"{overall.get('best_score', 0):.1f}%"
            )

        # ----------------------------------------------------
        # TOPIC MASTERY
        # ----------------------------------------------------

        if topics:

            st.subheader(
                "🧠 Topic Mastery"
            )

            for topic_data in topics:

                topic = topic_data.get(
                    "topic",
                    "Unknown"
                )

                average_score = float(
                    topic_data.get(
                        "average_score",
                        0
                    )
                )

                topic_attempts = topic_data.get(
                    "attempts",
                    0
                )

                best_score = float(
                    topic_data.get(
                        "best_score",
                        0
                    )
                )

                st.write(
                    f"**{topic}**"
                )

                st.progress(
                    min(
                        max(
                            average_score / 100,
                            0.0
                        ),
                        1.0
                    )
                )

                st.caption(
                    f"Average: {average_score:.1f}% "
                    f"• Attempts: {topic_attempts} "
                    f"• Best: {best_score:.1f}%"
                )

        # ----------------------------------------------------
        # QUIZ HISTORY
        # ----------------------------------------------------

        if attempts:

            st.subheader(
                "📚 Quiz History"
            )

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

                created_at = attempt.get(
                    "created_at",
                    ""
                )

                if score >= 80:

                    icon = "🟢"

                elif score >= 50:

                    icon = "🟡"

                else:

                    icon = "🔴"

                st.write(
                    f"{icon} **{topic}** — "
                    f"{score:.0f}%"
                )

                if created_at:

                    st.caption(
                        created_at
                    )

        else:

            st.info(
                "Complete your first quiz "
                "to start building your progress dashboard."
            )

    else:

        st.warning(
            f"Could not load learning progress "
            f"(HTTP {progress_response.status_code})."
        )

except requests.exceptions.ConnectionError:

    st.warning(
        "⚠️ Progress service is unavailable."
    )

except requests.exceptions.Timeout:

    st.warning(
        "⚠️ Progress request timed out."
    )

except Exception as error:

    st.warning(
        f"⚠️ Could not load progress: {error}"
    )
