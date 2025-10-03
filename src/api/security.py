
from fastapi import Header, HTTPException, Security
import os
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY',None)
api_key_header = APIKeyHeader(name='X-API-KEY', auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(status_code=403, detail='API key required')
    if api_key_header != API_KEY:
        raise HTTPException(status_code=403, detail='Invalid API Key')
    return api_key_header
