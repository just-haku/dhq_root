from mongoengine import connect, disconnect
from app.core.config import settings
import redis

# MongoDB Connection
def connect_db():
    """Connect to MongoDB"""
    connect(host=settings.MONGODB_URI, alias="default")

def disconnect_db():
    """Disconnect from MongoDB"""
    disconnect(alias="default")

# Redis Connection
import redis.asyncio as redis
redis_client = redis.from_url(settings.REDIS_URL)
