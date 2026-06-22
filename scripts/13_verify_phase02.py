"""Phase 02 end-to-end verification — checks reports, API, and Firestore."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


REPORTS = [
    "data/reports/confidence_report.json",
    "data/reports/explanation_report.json",
    "data/reports/drift_report.json",
    "data/reports/bias_report.json",
    "data/reports/contextual_report.json",
]

PASS = "[PASS]"
FAIL = "[FAIL]"


def check_reports():
    print("\n--- Phase 02 Report Files ---")
    all_ok = True
    for rel in REPORTS:
        p = ROOT / rel
        if not p.exists():
            print(f"  {FAIL} Missing: {rel}")
            all_ok = False
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            status = data.get("status", "?")
            print(f"  {PASS} {rel}  (status={status})")
        except Exception as e:
            print(f"  {FAIL} {rel} — invalid JSON: {e}")
            all_ok = False
    return all_ok


def check_api():
    print("\n--- FastAPI Backend ---")
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:8000/health", timeout=5) as r:
            body = json.loads(r.read())
        print(f"  {PASS} /health  →  {body}")
        return True
    except Exception as e:
        print(f"  {FAIL} Backend unreachable: {e}")
        print("        Start with: uvicorn src.api.main:app --reload")
        return False


def check_firestore():
    print("\n--- Firestore Collections ---")
    try:
        from src.database.firebase_client import get_firestore_client
        db = get_firestore_client()
        if db is None:
            print(f"  {FAIL} Firestore client not available (local fallback active)")
            return False

        collections = [
            "confidence_reports",
            "explanations",
            "drift_reports",
            "bias_reports",
            "contextual_reports",
        ]
        all_ok = True
        for col in collections:
            docs = list(db.collection(col).limit(1).stream())
            if docs:
                print(f"  {PASS} {col}  ({len(docs)} doc found)")
            else:
                print(f"  {FAIL} {col}  (empty — run corresponding script)")
                all_ok = False
        return all_ok
    except Exception as e:
        print(f"  {FAIL} Firestore check error: {e}")
        return False


def main():
    print("=" * 55)
    print("  PredictaGoal — Phase 02 Verification")
    print("=" * 55)

    r1 = check_reports()
    r2 = check_api()
    r3 = check_firestore()

    print("\n--- Summary ---")
    print(f"  Report files : {'OK' if r1 else 'ISSUES'}")
    print(f"  FastAPI      : {'OK' if r2 else 'ISSUES'}")
    print(f"  Firestore    : {'OK' if r3 else 'ISSUES'}")

    if r1 and r2 and r3:
        print("\n  All Phase 02 checks passed.")
        sys.exit(0)
    else:
        print("\n  Some checks failed — see details above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
