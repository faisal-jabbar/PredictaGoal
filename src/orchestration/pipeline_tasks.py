"""Callable pipeline tasks used by both Airflow DAGs and direct invocation."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from src.audit import audit_service

_ROOT = Path(__file__).resolve().parents[2]
_PYTHON = sys.executable


def _run_script(script_name: str) -> Dict[str, Any]:
    script_path = _ROOT / "scripts" / script_name
    result = subprocess.run(
        [_PYTHON, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(_ROOT),
    )
    success = result.returncode == 0
    return {
        "script": script_name,
        "success": success,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-800:] if result.stdout else "",
        "stderr_tail": result.stderr[-400:] if result.stderr else "",
    }


def task_check_environment() -> Dict[str, Any]:
    r = _run_script("01_check_environment.py")
    audit_service.log("system_startup", r)
    return r


def task_preprocess() -> Dict[str, Any]:
    r = _run_script("05_preprocess_data.py")
    audit_service.log("preprocessing", r)
    return r


def task_generate_features() -> Dict[str, Any]:
    r = _run_script("06_generate_features.py")
    audit_service.log("feature_generation", r)
    return r


def task_generate_confidence() -> Dict[str, Any]:
    r = _run_script("10_calculate_confidence.py")
    audit_service.log("confidence_calculated", r)
    return r


def task_generate_explanation() -> Dict[str, Any]:
    r = _run_script("09_generate_explanations.py")
    audit_service.log("explanation_generated", r)
    return r


def task_generate_drift() -> Dict[str, Any]:
    r = _run_script("11_generate_drift_report.py")
    audit_service.log("drift_detected", r)
    return r


def task_generate_bias() -> Dict[str, Any]:
    r = _run_script("12_generate_bias_report.py")
    audit_service.log("dashboard_report_read", {"report": "bias"})
    return r


def task_run_prediction_sample() -> Dict[str, Any]:
    r = _run_script("08_run_prediction.py")
    audit_service.log("prediction_generated", r)
    return r


def task_retrain_model() -> Dict[str, Any]:
    r = _run_script("07_train_model.py")
    audit_service.log("model_training", r)
    return r
