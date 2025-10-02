
from fastapi import APIRouter, Depends, Request
from src.api.limiter import limiter
from src.db.mongo import Mongo
from src.api.security import get_api_key

router = APIRouter()

@router.get('/', dependencies=[Depends(get_api_key)])
@limiter.limit("100/hour")
async def list_changes(request: Request, limit: int = 50):
    db = await Mongo.get_db()
    out = []
    cursor = db.change_log.find().sort('timestamp', -1).limit(limit)
    async for c in cursor:
        out.append(c)
    return out
