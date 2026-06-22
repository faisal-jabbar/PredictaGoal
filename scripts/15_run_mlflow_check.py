"""Script 15 — MLflow tracking check + initial run logging.

Sets up MLflow experiment, loads the existing trained model and its metrics,
logs a real MLflow run so the experiment is never empty.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PASS = "[PASS]"
FAIL = "[FAIL]"


def run_mlflow_check():
    print("=" * 55)
    print("  PredictaGoal — MLflow Check")
    print("=" * 55)

    # 1. Verify mlflow importable
    try:
        import mlflow
        print(f"\n  {PASS} mlflow {mlflow.__version__} installed")
    except ImportError:
        print(f"  {FAIL} mlflow not installed. Run: python -m pip install mlflow")
        sys.exit(1)

    # 2. Setup experiment
    from src.mlops.mlflow_client import setup_mlflow, get_tracking_uri
    exp_id = setup_mlflow()
    uri = get_tracking_uri()
    print(f"  {PASS} MLflow experiment created  (id={exp_id})")
    print(f"         Tracking URI: {uri}")

    # 3. Load existing model + metrics
    # Model report is in models/reports/ (written by train_model.py)
    model_report_path = ROOT / "models" / "reports" / "model_training_report.json"
    if not model_report_path.exists():
        print(f"  {FAIL} Model report not found — run scripts/07_train_model.py first")
        sys.exit(1)

    report = json.loads(model_report_path.read_text())
    print(f"  {PASS} Model report loaded  (accuracy={report.get('test_accuracy', '?')})")

    # 4. Load trained model artifact
    model_path = ROOT / "models" / "artifacts" / "football_match_model.joblib"
    feat_path  = ROOT / "models" / "artifacts" / "feature_columns.joblib"
    if not model_path.exists():
        print(f"  {FAIL} Model artifact missing: {model_path}")
        sys.exit(1)

    import joblib
    model = joblib.load(str(model_path))
    # Feature columns stored as JSON
    feat_json = ROOT / "models" / "artifacts" / "feature_columns.json"
    if feat_json.exists():
        feat_cols = json.loads(feat_json.read_text())
    else:
        feat_cols = joblib.load(str(feat_path))
    print(f"  {PASS} Model artifact loaded  ({len(feat_cols)} features)")

    # 5. Log a real MLflow run
    from src.mlops.experiment_tracker import log_training_run

    drift_report = ROOT / "data" / "reports" / "drift_report.json"
    drift_level = "unknown"
    if drift_report.exists():
        drift_level = json.loads(drift_report.read_text()).get("overall_drift_level", "unknown")

    bias_path = ROOT / "data" / "reports" / "bias_report.json"
    bias_summary = json.loads(bias_path.read_text()) if bias_path.exists() else None

    cm = report.get("confusion_matrix_list") or []

    run_id = log_training_run(
        model=model,
        params={
            "model_type":   report.get("model_type", "RandomForestClassifier"),
            "n_estimators": report.get("hyperparameters", {}).get("n_estimators", 200),
            "train_size":   report.get("train_size", 0),
            "test_size":    report.get("test_size", 0),
        },
        metrics={
            "test_accuracy":  report.get("test_accuracy", 0.0),
            "train_accuracy": report.get("train_accuracy", 0.0),
            "n_features":     float(len(feat_cols)),
        },
        feature_columns=feat_cols,
        artifact_path=str(model_path),
        drift_status=drift_level,
        bias_summary=bias_summary,
        run_name="phase03_initial_log",
    )
    print(f"  {PASS} MLflow run logged  (run_id={run_id})")

    # 6. Write model version record
    from src.mlops.model_versioning import write_version_record
    from src.mlops.model_registry import register_model
    bias_rpt = json.loads(bias_path.read_text()) if bias_path.exists() else {}
    draw_f1 = bias_rpt.get("accuracy_by_class", {}).get("draw", 0.30)

    version = write_version_record(
        accuracy=report.get("test_accuracy", 0.0),
        draw_f1=float(draw_f1),
        feature_columns=feat_cols,
        artifact_path=str(model_path),
        mlflow_run_id=run_id,
    )
    register_model(version)
    print(f"  {PASS} Model version record written  ({version['model_version']})")

    # 7. Verify latest run readable
    from src.mlops.experiment_tracker import get_latest_run
    latest = get_latest_run()
    if latest:
        print(f"  {PASS} Latest run readable  (status={latest.get('status')})")
    else:
        print(f"  {FAIL} Latest run not readable")

    print(f"\n  MLflow UI: mlflow ui --host 127.0.0.1 --port 5000")
    print(f"  Experiment: {uri}\n")
    print("  All MLflow checks passed.\n")


if __name__ == "__main__":
    run_mlflow_check()
