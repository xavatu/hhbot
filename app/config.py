from redis import Redis
from app.common.cache import RedisCache

redis_client = Redis(host="localhost", port=6379, db=0)
cache = RedisCache(redis_client)
