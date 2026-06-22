"""Agent tools — read local report files to build factual answers.

No hallucination. If data is missing, say so honestly.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

_ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> Optional[dict]:
    p = _ROOT / rel
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return None


def get_prediction() -> Optional[dict]:
    return _load("data/reports/sample_prediction.json")

def get_explanation() -> Optional[dict]:
    return _load("data/reports/explanation_report.json")

def get_confidence() -> Optional[dict]:
    return _load("data/reports/confidence_report.json")

def get_drift() -> Optional[dict]:
    return _load("data/reports/drift_report.json")

def get_bias() -> Optional[dict]:
    return _load("data/reports/bias_report.json")

def get_contextual() -> Optional[dict]:
    return _load("data/reports/contextual_report.json")

def get_model_report() -> Optional[dict]:
    return _load("models/reports/model_training_report.json")

def get_retraining_decision() -> Optional[dict]:
    return _load("data/reports/retraining_decision.json")

def get_model_version() -> Optional[dict]:
    return _load("data/reports/model_registry_report.json")
