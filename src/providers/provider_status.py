"""Aggregate status of all configured providers."""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.providers.kaggle_provider   import KaggleProvider
from src.providers.fixtures_provider import FixturesProvider
from src.providers.weather_provider  import WeatherProvider
from src.providers.injury_provider   import InjuryProvider

_ROOT = Path(__file__).resolve().parents[2]
_REPORT_PATH = _ROOT / "data" / "reports" / "provider_status_report.json"

_PROVIDERS = [KaggleProvider, FixturesProvider, WeatherProvider, InjuryProvider]


def get_all_statuses() -> dict:
    results = {}
    for cls in _PROVIDERS:
        p = cls()
        results[p.name] = p.health_check()

    report = {
        "providers": results,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(json.dumps(report, indent=2))

    try:
        from src.database import firestore_service
        firestore_service.write_document("provider_status", "latest", report)
    except Exception:
        pass

    return report
