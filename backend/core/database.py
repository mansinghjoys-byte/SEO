from motor.motor_asyncio import AsyncIOMotorClient
from .config import get_settings
import redis
from rq import Queue

settings = get_settings()

# MongoDB
mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
db = mongo_client[settings.DB_NAME]

# Redis
redis_client = redis.from_url(settings.REDIS_URL)
queue = Queue(connection=redis_client)

async def get_database():
    return db

def get_redis():
    return redis_client

def get_queue():
    return queue
