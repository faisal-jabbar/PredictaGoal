"""Report-related API routes."""
import os
import json
from fastapi import APIRouter
from src.api.schemas import ReportResponse
from src.config import settings

router = APIRouter()

REPORT_FILES = {
    "dataset":    os.path.join(settings.DATA_REPORTS_DIR, "data_quality_report.json"),
    "model":      os.path.join(settings.MODELS_REPORTS_DIR, "model_training_report.json"),
    "confidence": os.path.join(settings.DATA_REPORTS_DIR, "confidence_report.json"),
    "explanation":os.path.join(settings.DATA_REPORTS_DIR, "explanation_report.json"),
    "drift":      os.path.join(settings.DATA_REPORTS_DIR, "drift_report.json"),
    "bias":       os.path.join(settings.DATA_REPORTS_DIR, "bias_report.json"),
    "contextual": os.path.join(settings.DATA_REPORTS_DIR, "contextual_report.json"),
}


def _load(path: str):
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return None


def _report_route(report_type: str):
    path = REPORT_FILES.get(report_type)
    data = _load(path) if path else None
    if data is None:
        return ReportResponse(
            report_type=report_type,
            data={},
            available=False,
            error=f"Report not found. Run the corresponding Phase 02 script first.",
        )
    return ReportResponse(report_type=report_type, data=data, available=True)


@router.get("/reports/dataset",    response_model=ReportResponse)
def get_dataset_report():    return _report_route("dataset")

@router.get("/reports/model",      response_model=ReportResponse)
def get_model_report():      return _report_route("model")

@router.get("/reports/confidence", response_model=ReportResponse)
def get_confidence_report(): return _report_route("confidence")

@router.get("/reports/explanation",response_model=ReportResponse)
def get_explanation_report():return _report_route("explanation")

@router.get("/reports/drift",      response_model=ReportResponse)
def get_drift_report():      return _report_route("drift")

@router.get("/reports/bias",       response_model=ReportResponse)
def get_bias_report():       return _report_route("bias")

@router.get("/reports/contextual", response_model=ReportResponse)
def get_contextual_report(): return _report_route("contextual")
