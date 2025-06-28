import asyncio
import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import models.client  # noqa
import models.negotiation  # noqa
import models.resume  # noqa
from models.base import Base

TEST_DB_USER = os.getenv("TEST_DB_USER", "postgres")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "postgres")
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "hh_bot")
TEST_DB_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

async_engine = create_async_engine(TEST_DB_URL, echo=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def create_all():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    """
    checking some new sqla 2.0 features
    """
    loop = asyncio.new_event_loop()
    loop.run_until_complete(create_all())
    loop.close()
