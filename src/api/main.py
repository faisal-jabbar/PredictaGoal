"""
FastAPI Backend — PredictaGoal Phase 03 Production API.
Run with: uvicorn src.api.main:app --reload
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.api.routes_predictions import router as pred_router
from src.api.routes_reports     import router as report_router
from src.api.routes_phase03     import router as phase03_router
from src.api.schemas            import HealthResponse
from src.database.firebase_client import is_firebase_available
from src.monitoring.prometheus_metrics import initialise_gauges_from_reports
from src.audit import audit_service

app = FastAPI(
    title="PredictaGoal API",
    description="AI Football Match Prediction Agent — Phase 03 Production Agent",
    version="3.0.0",
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
app.include_router(phase03_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup():
    initialise_gauges_from_reports()
    audit_service.log("system_startup", {"event": "FastAPI startup", "version": "3.0.0"})


@app.get("/health", response_model=HealthResponse)
def health():
    fb_status = "connected" if is_firebase_available() else "unavailable (local fallback active)"
    return HealthResponse(status="ok", firebase=fb_status, version="3.0.0", phase="Phase 03")


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root():
    return {
        "project": "PredictaGoal",
        "phase": "Phase 03 — Production Agent",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }
