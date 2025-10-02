

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routes import books, changes
from src.db.mongo import Mongo
from src.scheduler.jobs import start_scheduler

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from src.api.limiter import limiter

app = FastAPI(title='FK Crawler API')
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)



app.include_router(books.router, prefix='/books', tags=['books'])
app.include_router(changes.router, prefix='/changes', tags=['changes'])


@app.on_event('startup')
async def startup():
    # initialize DB client
    db = await Mongo.get_db()
    # Ensure indexes for efficient querying and deduplication
    await db.books.create_index('url', unique=True)
    await db.books.create_index('category')
    await db.books.create_index('rating')
    await db.books.create_index('price_excluding_tax')
    await db.books.create_index('num_reviews')
    # start the scheduler in background (will run APScheduler loop)
    start_scheduler()

@app.get('/')
async def root():
    return {'message':'FK Crawler API up'}
