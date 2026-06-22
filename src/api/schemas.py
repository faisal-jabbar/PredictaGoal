"""Pydantic response schemas for the dashboard API."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    firebase: str
    version: str = "3.0.0"
    phase: str = "Phase 03"


class SummaryResponse(BaseModel):
    dataset_rows: Optional[int] = None
    cleaned_rows: Optional[int] = None
    model_accuracy: Optional[float] = None
    features_count: int = 14
    date_range_from: Optional[str] = None
    date_range_to: Optional[str] = None
    model_type: Optional[str] = None
    phase: str = "Phase 02 — Intelligence Dashboard"


class PredictionResponse(BaseModel):
    home_team: str
    away_team: str
    match_date: str
    tournament: Optional[str] = None
    prediction: str
    probabilities: Dict[str, float]
    confidence: float
    pcs: Optional[float] = None
    confidence_tier: Optional[str] = None
    confidence_note: Optional[str] = None


class ReportResponse(BaseModel):
    report_type: str
    data: Dict[str, Any]
    available: bool = True
    error: Optional[str] = None
