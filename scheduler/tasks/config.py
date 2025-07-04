import os

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.session import DB_URL
from scheduler.common.config import redis_host, redis_port

sync_engine = create_engine(DB_URL.replace("+asyncpg", ""))
sync_session = sessionmaker(sync_engine, expire_on_commit=False)
celery_app = Celery("auto_apply", broker=f"redis://{redis_host}:{redis_port}/0")

beat_max_loop_interval = os.getenv("BEAT_MAX_LOOP_INTERVAL", 300)
beat_max_loop_interval = int(beat_max_loop_interval)
celery_app.conf.update(
    beat_max_loop_interval=beat_max_loop_interval,
    redbeat_lock_timeout=beat_max_loop_interval * 5,
)
