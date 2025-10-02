
import pytest
from src.crawler.scraper import Scraper
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_crawl_index_small():
    async with AsyncClient() as client:
        s = Scraper('https://books.toscrape.com', client, concurrency=2)
        links = await s.crawl_index('https://books.toscrape.com/')
        assert isinstance(links, list)
