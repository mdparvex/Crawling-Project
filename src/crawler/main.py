
import asyncio
import os
from httpx import AsyncClient
from .scraper import Scraper
from dotenv import load_dotenv
from src.db.mongo import Mongo
from src.crawler.diff import compute_changes_and_log

load_dotenv()
BASE_URL = os.getenv('BASE_URL','https://books.toscrape.com')
CONCURRENCY = int(os.getenv('CRAWL_CONCURRENCY', '10'))

async def run_full_crawl(limit=None):
    from src.crawler.utils import retry_async
    async with AsyncClient(base_url=BASE_URL, timeout=20.0, follow_redirects=True) as client:
        scraper = Scraper(BASE_URL, client, concurrency=CONCURRENCY)
        links = await retry_async(lambda: scraper.crawl_index(BASE_URL))
        if limit:
            links = links[:limit]
        print(f'Found {len(links)} book links')
        db = await Mongo.get_db()
        progress_col = db.crawl_progress
        # Get set of already-processed URLs
        processed_urls = set()
        async for doc in progress_col.find({}, {'_id': 0, 'source_url': 1}):
            processed_urls.add(doc['source_url'])
        print(f'Skipping {len(processed_urls)} already-processed books')
        processed = 0
        for link in links:
            if link in processed_urls:
                continue
            try:
                book = await scraper.parse_book_page(link)
            except Exception as e:
                print(f'error processing {link}:', e)
                continue
            doc = book.model_dump(mode="json")
            existing = await db.books.find_one({'source_url': doc['source_url']})
            await db.books.update_one({'source_url': doc['source_url']}, {'$set': doc}, upsert=True)
            # Mark as processed
            await progress_col.insert_one({'source_url': link})
            await compute_changes_and_log(db, existing, doc)
            # Mark as processed
            processed += 1
            print(f'Processed {processed}/{len(links)}: {link}')
        print(f'Processed {processed} books')

if __name__ == '__main__':
    import asyncio, sys
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except:
            limit = None
    asyncio.run(run_full_crawl(limit=limit))
