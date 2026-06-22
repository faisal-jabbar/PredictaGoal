"""Script 14 — Airflow DAG structure check.

Validates that all three Airflow DAG files are present and syntactically importable.
Does NOT require Airflow to be installed — tests Python file validity only.
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAG_DIR = ROOT / "airflow" / "dags"

DAGS = [
    "predictagoal_daily_pipeline.py",
    "predictagoal_retraining_pipeline.py",
    "predictagoal_monitoring_pipeline.py",
]

PASS = "[PASS]"
FAIL = "[FAIL]"


def check_dag_syntax(filename: str) -> bool:
    p = DAG_DIR / filename
    if not p.exists():
        print(f"  {FAIL} Missing: airflow/dags/{filename}")
        return False
    try:
        source = p.read_text(encoding="utf-8")
        ast.parse(source)
        print(f"  {PASS} {filename}  (valid Python syntax)")
        return True
    except SyntaxError as e:
        print(f"  {FAIL} {filename}  syntax error: {e}")
        return False


def main():
    print("=" * 55)
    print("  PredictaGoal — Airflow DAG Check")
    print("=" * 55)
    print(f"\n  DAG directory: {DAG_DIR}\n")

    all_ok = all(check_dag_syntax(d) for d in DAGS)

    # Check orchestration + pipeline_tasks imports
    try:
        sys.path.insert(0, str(ROOT))
        from src.orchestration.retraining_decision import evaluate_retraining_need
        from src.orchestration.pipeline_tasks import task_check_environment
        from src.orchestration.scheduler_config import DAILY_PIPELINE_SCHEDULE
        print(f"\n  {PASS} src/orchestration imports OK")
        print(f"         Daily schedule: {DAILY_PIPELINE_SCHEDULE}")
    except Exception as e:
        print(f"\n  {FAIL} src/orchestration import failed: {e}")
        all_ok = False

    print("\n  Note: To run Airflow DAGs, install apache-airflow and")
    print("        set AIRFLOW_HOME, then: airflow standalone")

    if all_ok:
        print("\n  All Airflow DAG checks passed.\n")
        sys.exit(0)
    else:
        print("\n  Some checks failed.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
