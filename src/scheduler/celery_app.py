from celery import Celery
from celery.schedules import crontab
import os

celery_app = Celery(
    "scheduler",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "daily-detect": {
        "task": "tasks.detect_changes_job",
        "schedule": 86400.0,  # every 24 hours
    },
    "daily-report": {
        "task": "tasks.daily_report_job",
        "schedule": crontab(hour=0, minute=5),  # <-- FIXED
    },
}
