

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
from src.crawler.main import run_full_crawl
from src.db.mongo import Mongo
from src.scheduler.daily_report import generate_and_send_daily_change_report

scheduler = AsyncIOScheduler()


async def detect_changes_job():
    db = await Mongo.get_db()
    print('Starting change detection crawl at', datetime.utcnow())
    await run_full_crawl(limit=50)  # limit for daily run to be faster; adjust as needed
    print('Change detection crawl finished at', datetime.utcnow())

async def daily_report_job():
    print('Generating and sending daily change report...')
    await generate_and_send_daily_change_report()
    print('Daily change report sent.')


async def start_scheduler():
    try:
        scheduler.add_job(detect_changes_job, 'interval', hours=24, id='daily_detect', replace_existing=True)
        scheduler.add_job(daily_report_job, 'cron', hour=0, minute=5, id='daily_report', replace_existing=True)
    except Exception:
        pass
    scheduler.start()
    print('Scheduler started with jobs:', scheduler.get_jobs())
