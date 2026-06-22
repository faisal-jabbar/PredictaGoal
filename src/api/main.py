"""
FastAPI Backend — PredictaGoal Phase 02 Dashboard API.
Run with: uvicorn src.api.main:app --reload
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes_predictions import router as pred_router
from src.api.routes_reports import router as report_router
from src.api.schemas import HealthResponse
from src.database.firebase_client import is_firebase_available

app = FastAPI(
    title="PredictaGoal API",
    description="AI Football Match Prediction Agent — Phase 02 Intelligence Dashboard",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pred_router,    prefix="/api/v1")
app.include_router(report_router,  prefix="/api/v1")


@app.get("/health", response_model=HealthResponse)
def health():
    fb_status = "connected" if is_firebase_available() else "unavailable (local fallback active)"
    return HealthResponse(status="ok", firebase=fb_status)


@app.get("/")
def root():
    return {
        "project": "PredictaGoal",
        "phase": "Phase 02 — Intelligence Dashboard",
        "docs": "/docs",
        "health": "/health",
    }
