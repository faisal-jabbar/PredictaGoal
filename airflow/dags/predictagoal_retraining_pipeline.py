"""
PredictaGoal — Retraining Pipeline DAG
Runs at 02:00 UTC every Sunday (and can be triggered manually).
Reads drift report → decides → retrains if needed → evaluates → promotes if rules pass.
"""

import json
from datetime import timedelta
from pathlib import Path
import sys

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

from src.orchestration.scheduler_config import DEFAULT_ARGS, RETRAINING_SCHEDULE
from src.orchestration.retraining_decision import evaluate_retraining_need
from src.orchestration.pipeline_tasks import task_retrain_model
from src.audit import audit_service
from src.monitoring import prometheus_metrics


def _evaluate_drift(**ctx):
    decision = evaluate_retraining_need(force=False)
    ctx["task_instance"].xcom_push(key="decision", value=decision)
    return decision


def _branch_retrain(**ctx):
    decision = ctx["task_instance"].xcom_pull(task_ids="evaluate_drift", key="decision")
    if decision and decision.get("should_retrain"):
        return "retrain_model"
    return "skip_retraining"


def _do_retrain(**ctx):
    result = task_retrain_model()
    if not result.get("success"):
        raise RuntimeError(f"Retraining script failed: {result.get('stderr_tail', '')}")
    prometheus_metrics.retraining_decisions_total.labels(decision="retrain").inc()
    audit_service.log("retraining_triggered", result)
    return result


def _skip(**ctx):
    prometheus_metrics.retraining_decisions_total.labels(decision="skip").inc()
    audit_service.log("model_retraining_decision", {"decision": "no_retrain_needed"})


def _on_failure(ctx):
    audit_service.log("model_retraining_decision", {"dag": "retraining_pipeline", "status": "failed"})


_default = {**DEFAULT_ARGS, "on_failure_callback": _on_failure}

with DAG(
    dag_id="predictagoal_retraining_pipeline",
    default_args=_default,
    description="Weekly drift-triggered retraining: evaluate drift → decide → retrain → promote",
    schedule_interval=RETRAINING_SCHEDULE,
    start_date=days_ago(1),
    catchup=False,
    tags=["predictagoal", "retraining", "phase03"],
) as dag:

    t_evaluate = PythonOperator(task_id="evaluate_drift",  python_callable=_evaluate_drift)
    t_branch   = BranchPythonOperator(task_id="branch_retrain", python_callable=_branch_retrain)
    t_retrain  = PythonOperator(task_id="retrain_model",   python_callable=_do_retrain)
    t_skip     = PythonOperator(task_id="skip_retraining", python_callable=_skip)
    t_end      = EmptyOperator(task_id="pipeline_complete", trigger_rule="none_failed_min_one_success")

    t_evaluate >> t_branch >> [t_retrain, t_skip]
    t_retrain  >> t_end
    t_skip     >> t_end
