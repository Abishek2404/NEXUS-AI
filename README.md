# 🧠 NEXUS AI

> **Upload. Learn. Practice. Improve --- with AI.**

NEXUS AI is an AI-powered adaptive learning platform that transforms
personal study materials into an interactive learning experience. Users
can upload PDF course materials, build an AI-powered knowledge base, ask
questions using an AI Tutor, generate quizzes, evaluate performance,
track progress, and receive personalized learning plans.

## ✨ Features

-   📚 Upload and process PDF study materials
-   🤖 AI Tutor powered by retrieval-augmented generation (RAG)
-   📝 AI-generated multiple-choice quizzes
-   📊 Quiz performance analytics
-   🎯 Personalized adaptive learning plans
-   📈 Quiz attempt and progress tracking
-   🔎 Vector similarity search with ChromaDB

## 🏗️ Architecture

``` text
Streamlit Frontend
       │ HTTPS
       ▼
FastAPI Backend
   ┌───┼───────────────┐
   ▼   ▼               ▼
Gemini  ChromaDB   Progress Data
 AI     Vector DB
```

## 🛠️ Tech Stack

**Frontend:** Python, Streamlit

**Backend:** Python, FastAPI, Uvicorn, REST APIs

**AI:** Google Gemini, `gemini-embedding-001`, `gemini-2.5-flash`

**Document Processing:** PyMuPDF, text chunking

**Vector Search:** ChromaDB, embeddings, similarity search

**Deployment:** Streamlit Community Cloud, Render

## 📂 Project Structure

``` text
NEXUS-AI/
├── backend/
│   ├── api/
│   │   ├── analytics.py
│   │   ├── documents.py
│   │   ├── learning.py
│   │   ├── progress.py
│   │   ├── quiz.py
│   │   ├── search.py
│   │   └── tutor.py
│   ├── services/
│   │   ├── analytics_service.py
│   │   ├── chunk_service.py
│   │   ├── embedding_service.py
│   │   ├── learning_plan_service.py
│   │   ├── learning_service.py
│   │   ├── pdf_service.py
│   │   ├── progress_service.py
│   │   ├── quiz_service.py
│   │   ├── rag_service.py
│   │   └── vector_service.py
│   ├── data/
│   └── main.py
├── frontend/
│   └── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔌 API Endpoints

  Method   Endpoint                   Description
  -------- -------------------------- -------------------------------
  POST     `/documents/upload`        Upload and process a PDF
  POST     `/tutor/ask`               Ask the AI Tutor
  POST     `/quiz/generate`           Generate a quiz
  POST     `/analytics/evaluate`      Evaluate quiz performance
  POST     `/learning/plan`           Generate a learning plan
  POST     `/progress/attempt`        Save a quiz attempt
  GET      `/progress/{student_id}`   Retrieve student progress
  GET      `/health`                  Backend health check
  GET      `/docs`                    FastAPI Swagger documentation

## 🚀 Run Locally

### 1. Clone

``` bash
git clone https://github.com/Abishek2404/NEXUS-AI.git
cd NEXUS-AI
```

### 2. Install dependencies

``` bash
python -m venv venv
```

Windows:

``` bash
venv\Scriptsctivate
```

``` bash
pip install -r requirements.txt
```

### 3. Configure Gemini

Create `.env`:

``` env
GEMINI_API_KEY=your_gemini_api_key
```

Never commit API keys to GitHub.

### 4. Start FastAPI

``` bash
uvicorn backend.main:app --reload --reload-dir backend
```

Backend:

``` text
http://127.0.0.1:8000
```

Swagger:

``` text
http://127.0.0.1:8000/docs
```

### 5. Start Streamlit

In another terminal:

``` bash
streamlit run frontend/app.py
```

Frontend:

``` text
http://localhost:8501
```

## ☁️ Deployment

### Backend --- Render

Build command:

``` bash
pip install -r requirements.txt
```

Start command:

``` bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Environment variable:

``` text
GEMINI_API_KEY=your_gemini_api_key
```

### Frontend --- Streamlit Community Cloud

Deploy:

``` text
frontend/app.py
```

Configure Streamlit Secrets:

``` toml
API_URL = "https://your-backend-url.onrender.com"
```

Frontend code:

``` python
API_URL = st.secrets["API_URL"].rstrip("/")
```

## 🔄 Learning Workflow

``` text
PDF Upload
    ↓
PDF Text Extraction
    ↓
Text Chunking
    ↓
Embedding Generation
    ↓
ChromaDB Vector Storage
    ↓
AI Tutor / Quiz
    ↓
Relevant Content Retrieval
    ↓
AI Response / Quiz Evaluation
    ↓
Progress Tracking
    ↓
Adaptive Learning Plan
```

## 🔐 Security

-   Store Gemini API keys in environment variables or Streamlit Secrets.
-   Never commit `.env` files or secrets.
-   Use HTTPS for production APIs.
-   Configure CORS for the deployed frontend.
-   Use persistent production storage for vector and progress data.

## 🎯 Project Goal

NEXUS AI makes self-learning more interactive and personalized by
connecting a learner's own study materials with AI-powered tutoring,
assessment, analytics, and adaptive learning plans.

## 🌐 Current Deployment

**Frontend:** Streamlit Community Cloud

**Backend:** Render

**Backend URL:** `https://nexus-ai-bl3g.onrender.com`

## 👨‍💻 Author

**Abishek R**

B.Sc. Physics \| Web Development \| Data Science \| AI Applications

GitHub: https://github.com/Abishek2404

## 📄 License

This project is intended for educational and portfolio purposes.
