

from datetime import datetime
from typing import Dict, Any, List
import asyncio
from src.utils.alerting import send_alert_email

WATCH_FIELDS = ['title','description','price_including_tax','price_excluding_tax','availability','num_reviews','rating','image_url','category']

async def compute_changes_and_log(db, old_doc: Dict[str, Any], new_doc: Dict[str, Any]):
    """Compare old_doc and new_doc on WATCH_FIELDS and write entries to change_log collection."""
    if not old_doc:
        # new insertion: log as 'new' change type
        entry = {
            'book_url': new_doc.get('url'),
            'field': '__new__',
            'old': None,
            'new': new_doc,
            'timestamp': datetime.utcnow()
        }
        await db.change_log.insert_one(entry)
        # Send alert for new book
        subject = f"New Book Detected: {new_doc.get('title','(no title)')}"
        body = f"A new book was added.\nURL: {new_doc.get('url')}\nTitle: {new_doc.get('title')}\nCategory: {new_doc.get('category')}\nPrice: {new_doc.get('price_excluding_tax')}"
        asyncio.create_task(send_alert_email(subject, body))
        return [{'field':'__new__'}]
    changes = []
    for f in WATCH_FIELDS:
        old = old_doc.get(f)
        new = new_doc.get(f)
        # normalize simple types (strip strings)
        if isinstance(old, str):
            old_n = old.strip()
        else:
            old_n = old
        if isinstance(new, str):
            new_n = new.strip()
        else:
            new_n = new
        if old_n != new_n:
            change = {
                'book_url': new_doc.get('url'),
                'field': f,
                'old': old,
                'new': new,
                'timestamp': datetime.utcnow()
            }
            changes.append(change)
    if changes:
        await db.change_log.insert_many(changes)
        # Send alert for significant changes
        for change in changes:
            subject = f"Book Changed: {change['book_url']} ({change['field']})"
            body = f"Field: {change['field']}\nOld: {change['old']}\nNew: {change['new']}\nURL: {change['book_url']}\nTime: {change['timestamp']}"
            asyncio.create_task(send_alert_email(subject, body))
    return changes
