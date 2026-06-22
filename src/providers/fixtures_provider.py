"""Fixtures provider — fetches upcoming fixtures from external football API.

Requires FOOTBALL_API_KEY to be configured. If not set, returns disabled status.
Compatible with football-data.org or API-Football (RapidAPI) — configure via env.
"""

import os
from typing import Any, Dict, Optional

import requests

from src.providers.base_provider import BaseProvider


class FixturesProvider(BaseProvider):
    name = "fixtures"

    def __init__(self):
        self._key  = os.getenv("FOOTBALL_API_KEY", "")
        self._base = os.getenv("FOOTBALL_API_BASE_URL", "https://api.football-data.org/v4")

    def is_configured(self) -> bool:
        return bool(self._key)

    def _ping(self):
        resp = requests.get(
            f"{self._base}/competitions",
            headers={"X-Auth-Token": self._key},
            timeout=5,
        )
        resp.raise_for_status()

    def _fetch(self, competition: str = "WC", days_ahead: int = 7) -> Dict[str, Any]:
        try:
            from datetime import datetime, timedelta, timezone
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            until = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            resp = requests.get(
                f"{self._base}/competitions/{competition}/matches",
                headers={"X-Auth-Token": self._key},
                params={"dateFrom": today, "dateTo": until},
                timeout=10,
            )
            resp.raise_for_status()
            matches = resp.json().get("matches", [])
            return {"status": "ok", "count": len(matches), "matches": matches}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
