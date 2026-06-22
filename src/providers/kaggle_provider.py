"""Kaggle provider — wraps the existing KaggleHub dataset pipeline."""

import os
from typing import Any, Dict

from src.providers.base_provider import BaseProvider
from src.config.settings import kaggle_token_available


class KaggleProvider(BaseProvider):
    name = "kaggle"

    def is_configured(self) -> bool:
        return kaggle_token_available()

    def _fetch(self, dataset: str = "martj42/international-football-results-from-1872-to-2017") -> Dict[str, Any]:
        try:
            from src.ingestion.kaggle_loader import download_dataset
            path = download_dataset()
            return {"status": "ok", "path": str(path), "dataset": dataset}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def _ping(self):
        if not kaggle_token_available():
            raise RuntimeError("KAGGLE_API_TOKEN not set")
