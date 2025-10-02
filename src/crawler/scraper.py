
import asyncio
from typing import List
import httpx
from bs4 import BeautifulSoup
from .schema import Book
from .utils import fingerprint_from_html, retry_async
from urllib.parse import urljoin
import logging
logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, base_url: str, client: httpx.AsyncClient, concurrency: int = 10):
        self.base_url = base_url
        self.client = client
        self.semaphore = asyncio.Semaphore(concurrency)

    async def fetch(self, url: str) -> str:
        async def _do_fetch():
            async with self.semaphore:
                r = await self.client.get(url, timeout=20.0)
                r.raise_for_status()
                return r.text
        return await retry_async(_do_fetch)

    async def parse_book_page(self, url: str) -> Book:
        html = await self.fetch(url)
        soup = BeautifulSoup(html, 'lxml')
        title_tag = soup.select_one('div.product_main h1')
        title = title_tag.get_text(strip=True) if title_tag else 'Unknown'
        desc_tag = soup.select_one('#product_description')
        description = None
        if desc_tag:
            next_p = desc_tag.find_next_sibling('p')
            description = next_p.get_text(strip=True) if next_p else None
        category = None
        bc = soup.select('ul.breadcrumb li a')
        if bc and len(bc) >= 3:
            category = bc[-1].get_text(strip=True)
        image_rel = soup.select_one('.thumbnail img') or soup.select_one('div.carousel img')
        image_url = urljoin(self.base_url, image_rel['src']) if image_rel and image_rel.get('src') else None
        table = {}
        for row in soup.select('table.table-striped tr'):
            th = row.select_one('th')
            td = row.select_one('td')
            if th and td:
                table[th.get_text(strip=True)] = td.get_text(strip=True)
        def parse_price(s):
            try:
                return float(s.replace('£', '').strip())
            except:
                return None
        price_incl = parse_price(table.get('Price (incl. tax)','')) if 'Price (incl. tax)' in table else None
        price_excl = parse_price(table.get('Price (excl. tax)','')) if 'Price (excl. tax)' in table else None
        availability = table.get('Availability')
        num_reviews = None
        if 'Number of reviews' in table:
            try:
                num_reviews = int(table['Number of reviews'])
            except:
                num_reviews = None
        rating_tag = soup.select_one('p.star-rating')
        rating = None
        if rating_tag:
            classes = rating_tag.get('class', [])
            rating_map = {'One':1,'Two':2,'Three':3,'Four':4,'Five':5}
            for w in classes:
                if w in rating_map:
                    rating = rating_map[w]
        book = Book(
            url=url,
            title=title,
            description=description,
            category=category,
            price_including_tax=price_incl,
            price_excluding_tax=price_excl,
            availability=availability,
            num_reviews=num_reviews,
            image_url=image_url,
            rating=rating,
            source_url=url,
            raw_html=html,
            fingerprint=fingerprint_from_html(html)
        )
        return book

    async def crawl_index(self, index_url: str) -> List[str]:
        async def _do_crawl():
            html = await self.fetch(index_url)
            soup = BeautifulSoup(html, 'lxml')
            links = []
            for a in soup.select('article.product_pod h3 a'):
                href = a.get('href')
                links.append(urljoin(self.base_url, href))
            next_link = soup.select_one('li.next a')
            if next_link:
                next_url = urljoin(index_url, next_link['href'])
                rest = await self.crawl_index(next_url)
                links.extend(rest)
            return links
        return await retry_async(_do_crawl)
