"""
Local JSON fallback storage used when Firebase is unavailable.
"""
import os
from typing import Any

from src.utils.file_utils import ensure_dir, save_json
from src.utils.logger import get_logger

log = get_logger(__name__)


def save_local(data: Any, path: str) -> None:
    ensure_dir(os.path.dirname(path))
    save_json(data, path)
    log.info(f"Saved locally: {path}")


def ensure_fallback_dirs() -> None:
    from src.config import settings

    dirs = [
        settings.DATA_RAW_DIR,
        settings.DATA_PROCESSED_DIR,
        settings.DATA_REPORTS_DIR,
        settings.MODELS_ARTIFACTS_DIR,
        settings.MODELS_REPORTS_DIR,
        settings.LOGS_DIR,
    ]
    for d in dirs:
        ensure_dir(d)
    log.info("Local fallback directories verified.")
