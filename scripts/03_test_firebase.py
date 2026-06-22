"""
Script 03 — Firebase Connection Test.
Attempts a Firestore test write/read. Falls back gracefully if Firebase is unavailable.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.database.firebase_client import is_firebase_available, get_firestore_client

log = get_logger("03_test_firebase")

TEST_COLLECTION = "pipeline_logs"
TEST_DOC_ID = "connection_test"


def main():
    print("\n" + "=" * 60)
    print("  FIREBASE TEST — AI Football Match Prediction Agent")
    print("=" * 60)

    if not is_firebase_available():
        print("\n  Firebase credentials missing. Local fallback storage is active.")
        print("\n  To enable Firebase, fill in your .env file:")
        print("    FIREBASE_PROJECT_ID=your-project-id")
        print("    FIREBASE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com")
        print("    FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----")
        print("    (or set FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/service_account.json)")
        print("\n" + "=" * 60)
        print("  Result: Local fallback mode active. Firebase not tested.")
        print("=" * 60 + "\n")
        return

    print("\n  Firebase is available. Running write/read test …")
    db = get_firestore_client()

    try:
        test_data = {"status": "test", "message": "Firebase connection test", "agent": "football-ai"}
        db.collection(TEST_COLLECTION).document(TEST_DOC_ID).set(test_data)
        print("  Write test: OK")

        doc = db.collection(TEST_COLLECTION).document(TEST_DOC_ID).get()
        if doc.exists:
            print(f"  Read test:  OK — data: {doc.to_dict()}")
        else:
            print("  Read test:  FAILED — document not found after write")

        print("\n  Firebase connected successfully.")

    except Exception as exc:
        print(f"\n  Firebase test FAILED: {exc}")
        log.error(f"Firebase test failed: {exc}")

    print("\n" + "=" * 60)
    print("  Firebase test complete. Proceed to script 04.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
