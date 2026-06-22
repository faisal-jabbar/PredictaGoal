"""
Context service — orchestrates context building and storage.
"""
import os
from datetime import datetime
from typing import Dict, Any

from src.config import settings
from src.contextual.contextual_features import build_context
from src.database import firestore_service
from src.utils.file_utils import save_json
from src.utils.logger import get_logger

log = get_logger(__name__)

CONTEXTUAL_REPORT_PATH = os.path.join(settings.DATA_REPORTS_DIR, "contextual_report.json")


def run_contextual_report(prediction_result: Dict[str, Any]) -> Dict[str, Any]:
    ctx = build_context(
        home_team=prediction_result.get("home_team", ""),
        away_team=prediction_result.get("away_team", ""),
        tournament=prediction_result.get("tournament", "Unknown"),
        neutral=prediction_result.get("neutral_venue", False),
        match_date=str(prediction_result.get("match_date", "")),
    )

    report = {
        **ctx,
        "generated_at": datetime.utcnow().isoformat(),
        "notes": (
            "Context availability is determined by what fields exist in the "
            "Kaggle international football results dataset. "
            "Unavailable fields represent planned integrations, not application errors."
        ),
    }

    save_json(report, CONTEXTUAL_REPORT_PATH)
    log.info(f"Contextual report saved: {CONTEXTUAL_REPORT_PATH}")

    safe = _firestore_safe(report)
    firestore_service.write_document(
        "contextual_reports",
        "latest",
        safe,
        fallback_path=CONTEXTUAL_REPORT_PATH,
    )
    return report


def _firestore_safe(report: Dict) -> Dict:
    """Flatten nested dicts that contain complex objects for Firestore."""
    safe = {}
    for k, v in report.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            safe[k] = v
        elif isinstance(v, dict):
            # Flatten one level deep
            for dk, dv in v.items():
                if isinstance(dv, (str, int, float, bool)) or dv is None:
                    safe[f"{k}_{dk}"] = dv
                else:
                    safe[f"{k}_{dk}"] = str(dv)
        else:
            safe[k] = str(v)
    return safe
