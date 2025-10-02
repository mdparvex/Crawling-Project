
import asyncio, random
from hashlib import sha256

async def retry_async(fn, retries=3, base_delay=0.5):
    last_exc = None
    for i in range(retries):
        try:
            return await fn()
        except Exception as e:
            last_exc = e
            await asyncio.sleep(base_delay * (2 ** i) + random.random()*0.1)
    raise last_exc

def fingerprint_from_html(html: str) -> str:
    h = sha256()
    h.update(html.encode('utf-8'))
    return h.hexdigest()
