"""Email notifier — real SMTP if configured, otherwise logs locally only.

Set in .env:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
  ALERT_EMAIL_FROM, ALERT_EMAIL_TO
  ENABLE_EMAIL_ALERTS=true
"""

import os
import smtplib
import json
from email.mime.text import MIMEText
from datetime import datetime, timezone
from typing import Dict, Any


def _email_configured() -> bool:
    return (
        os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() == "true"
        and bool(os.getenv("SMTP_HOST"))
        and bool(os.getenv("SMTP_USER"))
        and bool(os.getenv("SMTP_PASSWORD"))
    )


def send_alert_email(subject: str, body: str) -> Dict[str, Any]:
    """Send alert email if SMTP configured. Returns status dict."""
    if not _email_configured():
        return {
            "sent": False,
            "reason": "Email alerts disabled — SMTP not configured. "
                      "Set ENABLE_EMAIL_ALERTS=true and SMTP credentials in .env.",
        }
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = f"[PredictaGoal Alert] {subject}"
        msg["From"] = os.getenv("ALERT_EMAIL_FROM", os.getenv("SMTP_USER"))
        msg["To"]   = os.getenv("ALERT_EMAIL_TO")

        host = os.getenv("SMTP_HOST")
        port = int(os.getenv("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
            smtp.send_message(msg)
        return {"sent": True, "to": msg["To"], "subject": msg["Subject"]}
    except Exception as e:
        return {"sent": False, "error": str(e)}
