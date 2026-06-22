"""
Script 02 — Database Setup.
Initialises Firebase if credentials are present, otherwise sets up local fallback.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.database.firebase_client import is_firebase_available
from src.database.local_storage import ensure_fallback_dirs

log = get_logger("02_setup_database")


def main():
    print("\n" + "=" * 60)
    print("  DATABASE SETUP — AI Football Match Prediction Agent")
    print("=" * 60)

    print("\n[1] Ensuring local fallback directories exist …")
    ensure_fallback_dirs()
    print("  Local fallback directories: OK")

    print("\n[2] Checking Firebase credentials …")
    from src.config import settings
    fb_available = settings.firebase_credentials_available()

    if fb_available:
        print("  Credentials found. Attempting Firebase connection …")
        available = is_firebase_available()
        if available:
            print("\n  Firebase connected successfully.")
        else:
            print("\n  Firebase credentials present but connection failed. Check credentials.")
    else:
        print("  Firebase credentials missing. Local fallback storage is active.")
        print("  To enable Firebase:")
        print("    1. Copy .env.example to .env")
        print("    2. Fill in FIREBASE_PROJECT_ID, FIREBASE_CLIENT_EMAIL, FIREBASE_PRIVATE_KEY")
        print("    3. Or set FIREBASE_SERVICE_ACCOUNT_PATH to your service account JSON file")

    print("\n" + "=" * 60)
    print("  Database setup complete. Proceed to script 03.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
