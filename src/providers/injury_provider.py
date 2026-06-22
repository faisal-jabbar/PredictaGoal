"""Injury/squad provider — fetches injury and suspension data.

Requires INJURY_API_KEY. If not set, returns honest disabled status.
No fake data is ever returned.
"""

import os
from typing import Any, Dict

import requests

from src.providers.base_provider import BaseProvider


class InjuryProvider(BaseProvider):
    name = "injury"

    def __init__(self):
        self._key  = os.getenv("INJURY_API_KEY", "")
        self._base = os.getenv("INJURY_API_BASE_URL", "")

    def is_configured(self) -> bool:
        return bool(self._key and self._base)

    def _ping(self):
        resp = requests.get(
            f"{self._base}/status",
            headers={"Authorization": f"Bearer {self._key}"},
            timeout=5,
        )
        resp.raise_for_status()

    def _fetch(self, team: str, match_date: str) -> Dict[str, Any]:
        try:
            resp = requests.get(
                f"{self._base}/injuries",
                headers={"Authorization": f"Bearer {self._key}"},
                params={"team": team, "date": match_date},
                timeout=10,
            )
            resp.raise_for_status()
            return {"status": "ok", "data": resp.json()}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
