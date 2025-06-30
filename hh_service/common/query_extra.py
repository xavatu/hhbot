from functools import wraps
from typing import Callable, Any, Coroutine

from fastapi import Request


def query_extra():
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        async_wrapper._query_extra = True
        return async_wrapper

    return decorator


def get_extra_params(request: Request):
    return dict(request.query_params)
