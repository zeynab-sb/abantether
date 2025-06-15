import redis
from django.conf import settings

redis_client = redis.StrictRedis(
    host=getattr(settings, "REDIS_HOST", "localhost"),
    port=getattr(settings, "REDIS_PORT", 6379),
    db=getattr(settings, "REDIS_DB", 0),
    decode_responses=True
)
