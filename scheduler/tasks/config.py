from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.session import DB_URL
from scheduler.common.config import redis_host, redis_port

sync_engine = create_engine(DB_URL.replace("+asyncpg", ""))
sync_session = sessionmaker(sync_engine, expire_on_commit=False)
celery_app = Celery("auto_apply", broker=f"redis://{redis_host}:{redis_port}/0")
