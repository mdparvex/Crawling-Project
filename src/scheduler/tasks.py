from .celery_app import celery_app
from datetime import datetime
from src.crawler.main import run_full_crawl
from src.scheduler.daily_report import generate_and_send_daily_change_report

@celery_app.task
def detect_changes_job():
    print(f"Starting change detection crawl at {datetime.now(__import__('datetime').timezone.utc)}")
    # call your async function from sync context
    import asyncio
    asyncio.run(run_full_crawl(limit=50))
    print(f"Change detection crawl finished at {datetime.now(__import__('datetime').timezone.utc)}")

@celery_app.task
def daily_report_job():
    print("Generating and sending daily change report...")
    import asyncio
    asyncio.run(generate_and_send_daily_change_report())
    print("Daily change report sent.")

