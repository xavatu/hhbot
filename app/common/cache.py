import functools
from typing import Protocol, Any, Optional, Hashable

from redis import Redis


class Cache(Protocol):
    def get(self, key: Hashable, *args, **kwargs) -> Optional[Any]:
        ...

    def set(self, key: Hashable, value: Any, *args, **kwargs) -> None:
        ...

    def is_expired(self, key: Hashable) -> bool:
        ...


def memoize(cache: Cache, **extra_args) -> Any:
    def decorator(func: Any) -> Any:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache_key = f"{func.__name__}:{args}:{frozenset(kwargs.items())}"
            cached_result = cache.get(cache_key)

            if cached_result:
                return cached_result

            result = func(*args, **kwargs)
            cache.set(cache_key, result, **extra_args)
            return result

        return wrapper

    return decorator


class DummyCache:
    def __init__(self):
        self.cache = {}

    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self.cache[key] = value

    def is_expired(self, key: str) -> bool:
        return False


class RedisCache:
    def __init__(self, redis_client: Redis):
        self._client = redis_client

    def get(self, key: str) -> Optional[Any]:
        value = self._client.get(key)
        return value

    def set(self, key: str, value: Any, expiration: int) -> None:
        self._client.setex(key, expiration, value)

    def is_expired(self, key: str) -> bool:
        ttl = self._client.ttl(key)
        return ttl == -2
