"""
PredictaGoal — Daily Pipeline DAG
Runs at 06:00 UTC every day.
Orchestrates: env check → preprocess → features → prediction →
confidence → explanation → drift → bias → audit → metrics.
"""

from datetime import timedelta
from pathlib import Path
import sys

# Allow importing project source when running under Airflow
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from src.orchestration.scheduler_config import DEFAULT_ARGS, DAILY_PIPELINE_SCHEDULE
from src.orchestration.pipeline_tasks import (
    task_check_environment,
    task_preprocess,
    task_generate_features,
    task_run_prediction_sample,
    task_generate_confidence,
    task_generate_explanation,
    task_generate_drift,
    task_generate_bias,
)
from src.audit import audit_service
from src.monitoring import prometheus_metrics


def _emit_pipeline_complete(**ctx):
    prometheus_metrics.pipeline_runs_total.labels(pipeline="daily", status="success").inc()
    audit_service.log("system_startup", {"dag": "daily_pipeline", "status": "complete"})


def _on_failure(ctx):
    task_id = ctx.get("task_instance", {}).task_id if hasattr(ctx.get("task_instance", {}), "task_id") else "unknown"
    audit_service.log("system_startup", {"dag": "daily_pipeline", "task": task_id, "status": "failed"})
    prometheus_metrics.pipeline_runs_total.labels(pipeline="daily", status="failure").inc()


_default = {**DEFAULT_ARGS, "on_failure_callback": _on_failure}

with DAG(
    dag_id="predictagoal_daily_pipeline",
    default_args=_default,
    description="Daily prediction pipeline: preprocess → features → predict → confidence → explain → drift → bias",
    schedule_interval=DAILY_PIPELINE_SCHEDULE,
    start_date=days_ago(1),
    catchup=False,
    tags=["predictagoal", "daily", "phase03"],
) as dag:

    t_env    = PythonOperator(task_id="check_environment",     python_callable=task_check_environment)
    t_pre    = PythonOperator(task_id="preprocess_data",       python_callable=task_preprocess)
    t_feat   = PythonOperator(task_id="generate_features",     python_callable=task_generate_features)
    t_pred   = PythonOperator(task_id="run_prediction_sample", python_callable=task_run_prediction_sample)
    t_conf   = PythonOperator(task_id="generate_confidence",   python_callable=task_generate_confidence)
    t_exp    = PythonOperator(task_id="generate_explanation",  python_callable=task_generate_explanation)
    t_drift  = PythonOperator(task_id="generate_drift",        python_callable=task_generate_drift)
    t_bias   = PythonOperator(task_id="generate_bias",         python_callable=task_generate_bias)
    t_done   = PythonOperator(task_id="emit_completion_event", python_callable=_emit_pipeline_complete)

    t_env >> t_pre >> t_feat >> t_pred >> t_conf >> t_exp >> t_drift >> t_bias >> t_done
