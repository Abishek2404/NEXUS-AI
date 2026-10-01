from fastapi import FastAPI

from backend.api.documents import router as documents_router
from backend.api.search import router as search_router
from backend.api.tutor import router as tutor_router
from backend.api.quiz import router as quiz_router
from backend.api.analytics import router as analytics_router
from backend.api.learning import router as learning_router
from backend.api.progress import router as progress_router


app = FastAPI(
    title="NEXUS AI",
    description="AI Adaptive Learning Platform",
    version="1.0.0"
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(documents_router)

app.include_router(search_router)

app.include_router(tutor_router)

app.include_router(quiz_router)

app.include_router(analytics_router)

app.include_router(learning_router)

app.include_router(progress_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to NEXUS AI",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }