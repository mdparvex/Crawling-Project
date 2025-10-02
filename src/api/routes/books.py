
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from src.api.limiter import limiter
from typing import Optional
from src.db.mongo import Mongo
from src.api.security import get_api_key

router = APIRouter()

@router.get('/', dependencies=[Depends(get_api_key)])
@limiter.limit("100/hour")
async def list_books(request: Request, category: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, rating: Optional[int] = None, sort_by: Optional[str] = None, page: int = 1, size: int = 20):
    db = await Mongo.get_db()
    q = {}
    if category:
        q['category'] = category
    if rating:
        q['rating'] = rating
    if min_price is not None or max_price is not None:
        price_q = {}
        if min_price is not None:
            price_q['$gte'] = min_price
        if max_price is not None:
            price_q['$lte'] = max_price
        q['price_excluding_tax'] = price_q
    cursor = db.books.find(q)
    if sort_by:
        if sort_by == 'price':
            cursor = cursor.sort('price_excluding_tax', 1)
        elif sort_by == 'rating':
            cursor = cursor.sort('rating', -1)
        elif sort_by == 'reviews':
            cursor = cursor.sort('num_reviews', -1)
    items = []
    async for d in cursor.skip((page-1)*size).limit(size):
        d['id'] = str(d.get('_id'))
        d.pop('_id', None)
        items.append(d)
    return {'items': items, 'page': page, 'size': size}

@router.get('/{book_id}', dependencies=[Depends(get_api_key)])
@limiter.limit("100/hour")
async def get_book(request: Request, book_id: str):
    db = await Mongo.get_db()
    from bson import ObjectId
    b = await db.books.find_one({'_id': ObjectId(book_id)})
    if not b:
        raise HTTPException(404, 'Not found')
    b['id'] = str(b['_id'])
    b.pop('_id', None)
    return b
