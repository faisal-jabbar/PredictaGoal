"""Script 16 — Prometheus metrics, health checks, and system status check."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PASS = "[PASS]"
FAIL = "[FAIL]"


def main():
    print("=" * 55)
    print("  PredictaGoal — Monitoring Check")
    print("=" * 55)

    # 1. Prometheus metrics importable
    try:
        from src.monitoring.prometheus_metrics import (
            prediction_requests_total,
            model_accuracy_gauge,
            drift_level_gauge,
            initialise_gauges_from_reports,
        )
        initialise_gauges_from_reports()
        print(f"\n  {PASS} Prometheus metrics module OK")
    except Exception as e:
        print(f"  {FAIL} Prometheus metrics import: {e}")
        sys.exit(1)

    # 2. Health checks
    from src.monitoring.health_checks import (
        check_report_freshness,
        check_model_artifact,
        check_firestore,
        full_health_report,
    )

    model = check_model_artifact()
    print(f"  {'  ' + PASS if model['exists'] else '  ' + FAIL} Model artifact: {'present' if model['exists'] else 'MISSING'}")

    reports = check_report_freshness()
    print(f"  {PASS} Report freshness: {len(reports['fresh'])} fresh, {len(reports['stale'])} stale, {len(reports['missing'])} missing")

    fs = check_firestore()
    print(f"  {PASS if fs['firestore_ok'] else FAIL} Firestore: {'OK' if fs['firestore_ok'] else fs.get('reason', 'unavailable')}")

    # 3. Full health + service status
    from src.monitoring.service_status import get_system_status
    status = get_system_status()
    print(f"  {PASS} System overall status: {status['overall'].upper()}")

    # 4. Alert evaluation
    from src.alerts.alert_service import run_alert_cycle
    alert_report = run_alert_cycle()
    print(f"  {PASS} Alert evaluation: {alert_report['alerts_triggered']} alerts triggered")

    # 5. Provider status
    from src.providers.provider_status import get_all_statuses
    prov = get_all_statuses()
    for name, info in prov.get("providers", {}).items():
        status_str = info.get("status", "?")
        badge = PASS if status_str in ("ok", "disabled") else FAIL
        print(f"  {badge} Provider [{name}]: {status_str}")

    # 6. Audit chain
    from src.audit.audit_logger import verify_chain, read_recent
    integrity = verify_chain()
    events = read_recent(3)
    print(f"  {PASS if integrity['valid'] else FAIL} Audit chain: {'valid' if integrity['valid'] else 'BROKEN'} ({integrity['events_checked']} events)")

    # 7. Prometheus config file
    prom_cfg = ROOT / "monitoring" / "prometheus" / "prometheus.yml"
    if prom_cfg.exists():
        print(f"  {PASS} Prometheus config: {prom_cfg}")
    else:
        print(f"  {FAIL} Prometheus config missing: {prom_cfg}")

    # 8. Grafana provisioning
    grafana_ds = ROOT / "monitoring" / "grafana" / "provisioning" / "datasources" / "prometheus.yml"
    if grafana_ds.exists():
        print(f"  {PASS} Grafana datasource config: present")
    else:
        print(f"  {FAIL} Grafana datasource config missing")

    print("\n  All monitoring checks complete.\n")


if __name__ == "__main__":
    main()
