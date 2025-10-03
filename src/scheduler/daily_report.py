import csv
import io
from datetime import datetime, timedelta
from src.db.mongo import Mongo
from src.utils.alerting import send_alert_email

async def generate_and_send_daily_change_report():
    db = await Mongo.get_db()
    # Get changes from the last 24 hours
    since = datetime.now(__import__('datetime').timezone.utc) - timedelta(days=1)
    cursor = db.change_log.find({'timestamp': {'$gte': since}})
    changes = [doc async for doc in cursor]
    if not changes:
        return  # No changes, no report
    # Prepare CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['book_url','field','old','new','timestamp'])
    writer.writeheader()
    for c in changes:
        writer.writerow({
            'book_url': c.get('book_url'),
            'field': c.get('field'),
            'old': c.get('old'),
            'new': c.get('new'),
            'timestamp': c.get('timestamp'),
        })
    csv_content = output.getvalue()
    output.close()
    # Send email with CSV attachment
    subject = f"Daily Book Change Report - {datetime.now(__import__('datetime').timezone.utc).date()}"
    body = "See attached CSV for today's book changes."
    await send_alert_email(subject, body, attachment=csv_content, filename="daily_change_report.csv")
