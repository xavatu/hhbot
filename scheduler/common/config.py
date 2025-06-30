import os

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_port = int(redis_port)
redis_url = f"redis://{redis_host}:{redis_port}/"
