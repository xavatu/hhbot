from fastapi import Request, Response
from redbeat import RedBeatSchedulerEntry
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from db.session import async_session
from scheduler.common.config import redis_url
from scheduler.common.cruds import AutoApplyConfigCRUD
from scheduler.common.schema import AutoApplyRedBeatTask
from scheduler.tasks.config import celery_app


class SyncRedBeatMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        async with async_session() as session:
            db_configs = await AutoApplyConfigCRUD.get_multi(session, {})
            db_tasks = {
                f"auto_apply_{c.id}": c for c in db_configs if c.enabled
            }

        redis_conn = Redis.from_url(redis_url, decode_responses=False)
        keys = await redis_conn.keys("redbeat:auto_apply_*")
        await redis_conn.aclose()

        redis_task_names = set(
            k.decode().replace("redbeat:", "")
            if isinstance(k, bytes)
            else k.replace("redbeat:", "")
            for k in keys
        )

        db_task_names = set(db_tasks.keys())
        to_add = db_task_names - redis_task_names
        to_remove = redis_task_names - db_task_names

        for task_name in to_add:
            config = db_tasks[task_name]
            task = AutoApplyRedBeatTask.model_validate(config)
            task.add_to_redbeat(celery_app)

        for task_name in to_remove:
            redbeat_key = f"redbeat:{task_name}"
            try:
                entry = RedBeatSchedulerEntry.from_key(
                    redbeat_key, app=celery_app
                )
                entry.delete()
            except Exception:
                raise

        return response
