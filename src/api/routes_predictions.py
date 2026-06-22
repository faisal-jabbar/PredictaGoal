"""Prediction-related API routes."""
import os
import json
from fastapi import APIRouter
from src.api.schemas import PredictionResponse, SummaryResponse
from src.config import settings
from src.utils.logger import get_logger

log = get_logger(__name__)
router = APIRouter()


def _load_json(path: str):
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return None


@router.get("/summary", response_model=SummaryResponse)
def get_summary():
    quality = _load_json(os.path.join(settings.DATA_REPORTS_DIR, "data_quality_report.json")) or {}
    model_r = _load_json(os.path.join(settings.MODELS_REPORTS_DIR, "model_training_report.json")) or {}
    dataset = _load_json(os.path.join(settings.DATA_REPORTS_DIR, "dataset_summary.json")) or {}

    date_range = quality.get("date_range", {})
    return SummaryResponse(
        dataset_rows=quality.get("total_rows_loaded"),
        cleaned_rows=quality.get("final_usable_rows"),
        model_accuracy=model_r.get("accuracy"),
        features_count=len(model_r.get("feature_columns", [])) or 14,
        date_range_from=date_range.get("from"),
        date_range_to=date_range.get("to"),
        model_type=model_r.get("model_type"),
    )


@router.get("/predictions/sample", response_model=PredictionResponse)
def get_sample_prediction():
    pred = _load_json(os.path.join(settings.DATA_REPORTS_DIR, "sample_prediction.json")) or {}
    conf = _load_json(os.path.join(settings.DATA_REPORTS_DIR, "confidence_report.json")) or {}

    return PredictionResponse(
        home_team=pred.get("home_team", "Brazil"),
        away_team=pred.get("away_team", "Argentina"),
        match_date=str(pred.get("match_date", "2017-06-01")),
        tournament=pred.get("tournament"),
        prediction=pred.get("prediction", "unknown"),
        probabilities=pred.get("probabilities", {}),
        confidence=pred.get("confidence", 0.0),
        pcs=conf.get("pcs"),
        confidence_tier=conf.get("confidence_tier"),
        confidence_note=conf.get("confidence_note"),
    )
