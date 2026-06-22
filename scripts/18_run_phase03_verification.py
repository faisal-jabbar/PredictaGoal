"""Script 18 — Final Phase 03 end-to-end verification.

Checks Phase 01, Phase 02, and Phase 03 components.
"""

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

_results = {"pass": 0, "fail": 0, "warn": 0}


def ok(msg):
    print(f"  {PASS} {msg}")
    _results["pass"] += 1


def fail(msg):
    print(f"  {FAIL} {msg}")
    _results["fail"] += 1


def warn(msg):
    print(f"  {WARN} {msg}")
    _results["warn"] += 1


def section(title):
    print(f"\n--- {title} ---")


def check_file(rel, label=None):
    p = ROOT / rel
    label = label or rel
    if p.exists() and p.stat().st_size > 0:
        ok(label)
        return True
    fail(f"Missing or empty: {label}")
    return False


def check_json(rel, label=None):
    p = ROOT / rel
    label = label or rel
    if not p.exists():
        fail(f"Missing: {label}")
        return False
    try:
        json.loads(p.read_text())
        ok(label)
        return True
    except Exception as e:
        fail(f"Invalid JSON: {label} — {e}")
        return False


def check_url(url, label, key=None, expected=None, timeout=8):
    try:
        import urllib.request as _ur
        with _ur.urlopen(url, timeout=timeout) as r:
            data = json.loads(r.read())
        if key and expected and data.get(key) != expected:
            warn(f"{label} responded but {key}={data.get(key)} (expected {expected})")
        else:
            ok(f"{label} = {data.get(key or 'status', 'ok')}")
        return data
    except Exception as e:
        fail(f"{label} unreachable: {e}")
        return None


def main():
    print("=" * 60)
    print("  PredictaGoal — Phase 03 Final Verification")
    print("=" * 60)

    # ── Phase 01 ──────────────────────────────────────────────
    section("Phase 01 — Core Pipeline")
    check_file("models/artifacts/football_match_model.joblib",  "Trained model artifact")
    check_file("models/artifacts/feature_columns.json",          "Feature columns")
    check_json("models/reports/model_training_report.json",      "Model training report")
    check_json("data/reports/sample_prediction.json",            "Sample prediction report")
    check_json("data/reports/data_quality_report.json",          "Data quality report")
    check_file("data/processed/matches_processed.csv",           "Processed dataset")

    # ── Phase 02 ──────────────────────────────────────────────
    section("Phase 02 — Intelligence Dashboard")
    for f in ["confidence", "explanation", "drift", "bias", "contextual"]:
        check_json(f"data/reports/{f}_report.json", f"{f}_report.json")

    # ── Phase 03 Reports ──────────────────────────────────────
    section("Phase 03 — Reports & Artifacts")
    check_json("data/reports/retraining_decision.json",    "Retraining decision report")
    check_json("data/reports/model_registry_report.json",  "Model registry report")
    check_json("data/reports/provider_status_report.json", "Provider status report")
    check_json("data/reports/system_health_report.json",   "System health report")
    check_json("data/reports/alerts_report.json",          "Alerts report")
    check_json("data/reports/agent_query_report.json",     "Agent query report")
    check_file("data/audit/audit_log.jsonl",               "Audit log (JSONL)")
    check_json("models/reports/model_version.json",        "Model version record")

    # ── Audit chain integrity ─────────────────────────────────
    section("Audit Trail Integrity")
    try:
        from src.audit.audit_logger import verify_chain, read_recent
        integrity = verify_chain()
        events = read_recent(3)
        if integrity["valid"]:
            ok(f"Hash chain valid ({integrity['events_checked']} events)")
        else:
            fail(f"Hash chain BROKEN at index {integrity.get('broken_at_index')}")
    except Exception as e:
        fail(f"Audit check failed: {e}")

    # ── FastAPI Endpoints ──────────────────────────────────────
    section("FastAPI Backend Endpoints")
    health = check_url("http://localhost:8000/health", "/health", "status", "ok")
    if health:
        ok(f"  Firebase: {health.get('firebase', '?')}")

    check_url("http://localhost:8000/api/v1/summary",              "/api/v1/summary")
    check_url("http://localhost:8000/api/v1/predictions/sample",   "/api/v1/predictions/sample")
    check_url("http://localhost:8000/api/v1/system/status",        "/api/v1/system/status",  timeout=15)
    check_url("http://localhost:8000/api/v1/providers/status",     "/api/v1/providers/status")
    check_url("http://localhost:8000/api/v1/agent/capabilities",   "/api/v1/agent/capabilities")
    check_url("http://localhost:8000/api/v1/retraining/status",    "/api/v1/retraining/status")
    check_url("http://localhost:8000/api/v1/model/version",        "/api/v1/model/version")
    check_url("http://localhost:8000/api/v1/audit/recent",         "/api/v1/audit/recent")
    check_url("http://localhost:8000/api/v1/alerts/recent",        "/api/v1/alerts/recent")

    # Prometheus metrics endpoint
    try:
        import urllib.request as _ur2
        with _ur2.urlopen("http://localhost:8000/metrics", timeout=5) as r:
            body = r.read().decode()
        if "predictagoal_" in body:
            ok("/metrics (Prometheus metrics present)")
        else:
            warn("/metrics reachable but no predictagoal_ metrics yet")
    except Exception as e:
        fail(f"/metrics unreachable: {e}")

    # ── Agent query ────────────────────────────────────────────
    section("Agent Query (POST /api/v1/agent/query)")
    try:
        import urllib.parse
        data = json.dumps({"query": "What is the latest prediction?"}).encode()
        req = urllib.request.Request(
            "http://localhost:8000/api/v1/agent/query",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read())
        intent = resp.get("intent", "?")
        ok(f"Agent query responded (intent={intent})")
    except Exception as e:
        fail(f"Agent query failed: {e}")

    # ── MLflow ────────────────────────────────────────────────
    section("MLflow")
    try:
        from src.mlops.experiment_tracker import get_latest_run
        run = get_latest_run()
        if run:
            ok(f"Latest MLflow run: {run.get('run_id', '?')[:12]}... status={run.get('status')}")
        else:
            warn("No MLflow runs found — run script 15 first")
    except Exception as e:
        fail(f"MLflow check failed: {e}")

    mlruns = ROOT / "mlruns"
    if mlruns.exists() and any(mlruns.iterdir()):
        ok("mlruns/ directory contains experiment data")
    else:
        warn("mlruns/ is empty")

    # ── Firestore collections ─────────────────────────────────
    section("Firestore Collections (Phase 03)")
    try:
        from src.database.firebase_client import get_firestore_client
        db = get_firestore_client()
        if db is None:
            warn("Firestore unavailable (local fallback active)")
        else:
            phase03_cols = [
                "audit_events", "alerts", "alert_events", "user_preferences",
                "model_versions", "model_registry", "retraining_decisions",
                "provider_status", "agent_queries",
            ]
            for col in phase03_cols:
                docs = list(db.collection(col).limit(1).stream())
                if docs:
                    ok(f"Collection: {col}")
                else:
                    warn(f"Collection empty: {col}")
    except Exception as e:
        fail(f"Firestore check: {e}")

    # ── Infrastructure files ───────────────────────────────────
    section("Infrastructure Files")
    check_file("docker-compose.yml",                                          "docker-compose.yml")
    check_file("docker/backend.Dockerfile",                                   "backend.Dockerfile")
    check_file("docker/frontend.Dockerfile",                                  "frontend.Dockerfile")
    check_file("docker/airflow.Dockerfile",                                   "airflow.Dockerfile")
    check_file(".dockerignore",                                               ".dockerignore")
    check_file("airflow/dags/predictagoal_daily_pipeline.py",                "Daily DAG")
    check_file("airflow/dags/predictagoal_retraining_pipeline.py",           "Retraining DAG")
    check_file("airflow/dags/predictagoal_monitoring_pipeline.py",           "Monitoring DAG")
    check_file("monitoring/prometheus/prometheus.yml",                        "Prometheus config")
    check_file("monitoring/grafana/provisioning/datasources/prometheus.yml",  "Grafana datasource")
    check_file("monitoring/grafana/provisioning/dashboards/dashboard.yml",    "Grafana dashboard provisioning")
    check_file("monitoring/grafana/dashboards/predictagoal-dashboard.json",  "Grafana dashboard JSON")

    # ── Security check ────────────────────────────────────────
    section("Security — No secrets committed")
    try:
        import subprocess
        tracked = subprocess.check_output(
            ["git", "ls-files"], cwd=str(ROOT), stderr=subprocess.DEVNULL
        ).decode()
        secret_patterns = [".env\n", "secrets/", "service_account", "node_modules", "dist/", "data/raw/"]
        found_secrets = [p for p in secret_patterns if p in tracked or p.rstrip("/") in tracked.replace("\r\n", "\n")]
        if not found_secrets:
            ok("No secrets or artifacts tracked by git")
        else:
            for s in found_secrets:
                fail(f"Potentially sensitive tracked: {s.strip()}")
    except Exception as e:
        warn(f"Git security check skipped: {e}")

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    p, f, w = _results["pass"], _results["fail"], _results["warn"]
    print(f"  PASSED: {p}  |  FAILED: {f}  |  WARNINGS: {w}")
    if f == 0:
        print("  Phase 03 verification COMPLETE — all checks passed.\n")
        sys.exit(0)
    else:
        print(f"  {f} check(s) failed — see details above.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
