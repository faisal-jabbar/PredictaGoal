"""Scheduler configuration — shared constants for Airflow DAGs."""

DAILY_PIPELINE_SCHEDULE   = "0 6 * * *"    # 06:00 UTC daily
RETRAINING_SCHEDULE       = "0 2 * * 0"    # 02:00 UTC every Sunday
MONITORING_SCHEDULE       = "*/30 * * * *" # Every 30 minutes

DAG_OWNER         = "predictagoal"
DAG_RETRIES       = 3
DAG_RETRY_DELAY_M = 5  # minutes

DEFAULT_ARGS = {
    "owner": DAG_OWNER,
    "depends_on_past": False,
    "retries": DAG_RETRIES,
    "email_on_failure": False,
    "email_on_retry": False,
}
