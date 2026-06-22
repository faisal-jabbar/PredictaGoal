"""
Firebase Admin SDK initialisation.
Returns a connected Firestore client or None if credentials are missing.
"""
import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore

from src.config import settings
from src.utils.logger import get_logger

log = get_logger(__name__)

_db: Optional[object] = None
_initialized: bool = False
_available: bool = False


def _init_firebase() -> bool:
    global _db, _initialized, _available

    if _initialized:
        return _available

    _initialized = True

    if not settings.firebase_credentials_available():
        log.warning("Firebase credentials missing. Local fallback storage is active.")
        _available = False
        return False

    try:
        if not firebase_admin._apps:
            if settings.FIREBASE_SERVICE_ACCOUNT_PATH and os.path.isfile(
                settings.FIREBASE_SERVICE_ACCOUNT_PATH
            ):
                cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
            else:
                cred = credentials.Certificate(
                    {
                        "type": "service_account",
                        "project_id": settings.FIREBASE_PROJECT_ID,
                        "client_email": settings.FIREBASE_CLIENT_EMAIL,
                        "private_key": settings.FIREBASE_PRIVATE_KEY,
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                )
            firebase_admin.initialize_app(cred)

        _db = firestore.client()
        _available = True
        log.info("Firebase connected successfully.")
        return True

    except Exception as exc:
        log.error(f"Firebase initialisation failed: {exc}")
        _available = False
        return False


def get_firestore_client() -> Optional[object]:
    _init_firebase()
    return _db if _available else None


def is_firebase_available() -> bool:
    _init_firebase()
    return _available
