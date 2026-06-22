"""
PredictaGoal — Monitoring Pipeline DAG
Runs every 30 minutes.
Checks backend health, Firestore, report freshness, and emits Prometheus metrics.
"""

from datetime import timedelta
from pathlib import Path
import sys

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from src.orchestration.scheduler_config import DEFAULT_ARGS, MONITORING_SCHEDULE
from src.monitoring import health_checks, prometheus_metrics
from src.audit import audit_service


def _check_backend(**ctx):
    result = health_checks.check_api_health()
    prometheus_metrics.firestore_up.set(1 if result.get("firebase") == "connected" else 0)
    audit_service.log("api_health_check", result)
    if not result.get("api_ok"):
        raise RuntimeError("FastAPI backend is unreachable.")
    return result


def _check_reports(**ctx):
    result = health_checks.check_report_freshness()
    prometheus_metrics.stale_reports_count.set(result.get("stale_count", 0))
    return result


def _check_model(**ctx):
    result = health_checks.check_model_artifact()
    return result


def _emit_health(**ctx):
    report = health_checks.full_health_report()
    from src.database import firestore_service
    try:
        firestore_service.write_document("system_health", "latest", report)
    except Exception:
        pass
    return report


def _on_failure(ctx):
    audit_service.log("api_health_check", {"dag": "monitoring_pipeline", "status": "failed"})


_default = {**DEFAULT_ARGS, "retries": 1, "on_failure_callback": _on_failure}

with DAG(
    dag_id="predictagoal_monitoring_pipeline",
    default_args=_default,
    description="Health checks every 30 minutes: API, Firestore, report freshness, model artifact",
    schedule_interval=MONITORING_SCHEDULE,
    start_date=days_ago(1),
    catchup=False,
    tags=["predictagoal", "monitoring", "phase03"],
) as dag:

    t_api     = PythonOperator(task_id="check_backend_health",  python_callable=_check_backend)
    t_reports = PythonOperator(task_id="check_report_freshness", python_callable=_check_reports)
    t_model   = PythonOperator(task_id="check_model_artifact",  python_callable=_check_model)
    t_emit    = PythonOperator(task_id="emit_health_report",    python_callable=_emit_health)

    [t_api, t_reports, t_model] >> t_emit
