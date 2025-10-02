import logging
import asyncio
from src.db.mongo import Mongo

class MongoHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.loop = asyncio.get_event_loop()

    def emit(self, record):
        # Use loop.create_task to schedule DB write
        try:
            msg = self.format(record)
            log_doc = {
                'level': record.levelname,
                'message': msg,
                'name': record.name,
                'created': record.created,
                'pathname': record.pathname,
                'lineno': record.lineno,
                'funcName': record.funcName,
            }
            self.loop.create_task(self._write_log(log_doc))
        except Exception:
            self.handleError(record)

    async def _write_log(self, log_doc):
        db = await Mongo.get_db()
        await db.logs.insert_one(log_doc)
