
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI','mongodb://localhost:27017')
MONGO_DB = os.getenv('MONGO_DB','fk_crawler')

class Mongo:
    _client = None

    @classmethod
    async def get_client(cls):
        if not cls._client:
            cls._client = AsyncIOMotorClient(MONGO_URI)
        return cls._client

    @classmethod
    async def get_db(cls):
        client = await cls.get_client()
        return client[MONGO_DB]
