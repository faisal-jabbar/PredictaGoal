"""Weather provider — fetches venue weather context.

Uses Open-Meteo (free, no key required) if WEATHER_API_KEY is empty.
Falls back to disabled if lat/lon coordinates are not available.
"""

import os
from typing import Any, Dict, Optional

import requests

from src.providers.base_provider import BaseProvider

_OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"


class WeatherProvider(BaseProvider):
    name = "weather"

    def __init__(self):
        self._key  = os.getenv("WEATHER_API_KEY", "")
        self._base = os.getenv("WEATHER_API_BASE_URL", "")

    def is_configured(self) -> bool:
        # Open-Meteo is free — provider is available without a key
        return True

    def health_check(self) -> Dict[str, Any]:
        try:
            self._ping()
            return {"provider": self.name, "status": "ok", "source": "open-meteo (free)"}
        except Exception as e:
            return {"provider": self.name, "status": "error", "reason": str(e)}

    def _ping(self):
        requests.get(_OPEN_METEO_BASE, params={"latitude": 0, "longitude": 0, "hourly": "temperature_2m"}, timeout=5).raise_for_status()

    def _fetch(self, latitude: float, longitude: float, date: Optional[str] = None) -> Dict[str, Any]:
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,precipitation_sum,windspeed_10m_max",
                "timezone": "UTC",
                "forecast_days": 1,
            }
            if date:
                params["start_date"] = date
                params["end_date"] = date
            resp = requests.get(_OPEN_METEO_BASE, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json().get("daily", {})
            return {
                "status": "ok",
                "source": "open-meteo",
                "temperature_max_c": (data.get("temperature_2m_max") or [None])[0],
                "precipitation_mm": (data.get("precipitation_sum") or [None])[0],
                "wind_speed_kmh": (data.get("windspeed_10m_max") or [None])[0],
                "latitude": latitude,
                "longitude": longitude,
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def fetch(self, *args, **kwargs) -> Dict[str, Any]:
        if "latitude" not in kwargs and not args:
            return {
                "status": "disabled",
                "reason": "latitude and longitude coordinates required — not available from current dataset",
            }
        return self._fetch(*args, **kwargs)
