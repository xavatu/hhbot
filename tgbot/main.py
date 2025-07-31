import asyncio
import json
import os
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, Router, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LoginUrl,
)
from redis.asyncio import Redis
from sqlalchemy import select

from db.models import Session
from db.session import async_session

API_TOKEN = os.getenv("API_TOKEN")
OAUTH_URL = os.getenv("OAUTH_URL")
OAUTH_TIMEOUT = int(os.getenv("OAUTH_TIMEOUT", 10))
SESSION_MAX_AGE = int(os.getenv("SESSION_MAX_AGE", 14 * 24 * 60 * 60))

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_port = int(redis_port)
redis_url = f"redis://{redis_host}:{redis_port}/"

router = Router()


async def fetch_session_from_db(
    telegram_id: int, max_age_sec: int = 600
) -> Session | None:
    since = datetime.now(timezone.utc) - timedelta(seconds=max_age_sec)
    async with async_session() as db:
        stmt = (
            select(Session)
            .where(Session.telegram_id == telegram_id)
            .where(Session.created_at >= since)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


async def get_session(redis_conn, telegram_id: int) -> Session | None:
    cached = await redis_conn.get(f"session:{telegram_id}")
    if cached:
        data = json.loads(cached)
        session = Session(
            id=data["id"],
            client_id=data["client_id"],
            telegram_id=data["telegram_id"],
            token=data["token"],
            state=data.get("state"),
            status=data.get("status", "pending"),
            encoded=data.get("encoded"),
            mode=data.get("mode", "web"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
        return session

    session = await fetch_session_from_db(
        telegram_id, max_age_sec=SESSION_MAX_AGE
    )
    if session:
        await redis_conn.set(
            f"session:{telegram_id}",
            json.dumps(
                {
                    "id": session.id,
                    "client_id": session.client_id,
                    "telegram_id": session.telegram_id,
                    "token": session.token,
                    "state": session.state,
                    "status": session.status,
                    "encoded": session.encoded,
                    "mode": session.mode,
                    "created_at": session.created_at.isoformat(),
                }
            ),
            ex=SESSION_MAX_AGE,
        )
    return session


async def wait_for_authorization(
    redis_conn: Redis, telegram_id: int, timeout: int
):
    interval = 3
    attempts = timeout // interval

    for _ in range(attempts):
        session = await get_session(redis_conn, telegram_id)
        if session:
            return session
        await asyncio.sleep(interval)

    return None


class SessionMiddleware(BaseMiddleware):
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    async def __call__(self, handler, event, data):
        if (
            hasattr(event, "text")
            and event.text
            and event.text.startswith(("/start", "/auth"))
        ):
            return await handler(event, data)

        telegram_id = event.from_user.id
        session = await get_session(self.redis_conn, telegram_id)

        if not session:
            await event.answer(
                "Сессия не найдена или устарела. Авторизуйтесь заново."
            )
            return None

        data["session"] = session
        return await handler(event, data)


@router.message(Command("start", "auth"))
async def cmd_start(message: Message):
    telegram_id = message.from_user.id
    login_url = LoginUrl(
        url=f"{OAUTH_URL}?mode=telegram",
        forward_text="Войти через Telegram",
        request_write_access=True,
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Войти через Telegram", login_url=login_url
                )
            ]
        ]
    )

    await message.answer(
        "Нажмите кнопку ниже для авторизации через Telegram:",
        reply_markup=keyboard,
    )
    await message.answer("Ожидаю подтверждения авторизации...")

    redis_conn = await Redis.from_url(redis_url, decode_responses=True)
    session = await wait_for_authorization(
        redis_conn, telegram_id, OAUTH_TIMEOUT
    )
    if session:
        await message.answer("Авторизация прошла успешно.")
    else:
        await message.answer("Время ожидания истекло. Попробуйте ещё раз.")

    await redis_conn.aclose()


@router.message(Command("profile"))
async def profile_handler(message: Message, session: Session):
    await message.answer(f"Ваша сессия: {session.id}")


async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    redis_conn = await Redis.from_url(redis_url, decode_responses=True)
    dp.message.middleware(SessionMiddleware(redis_conn))
    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await redis_conn.aclose()


if __name__ == "__main__":
    asyncio.run(main())
