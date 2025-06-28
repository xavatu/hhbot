from aiohttp import ClientSession, CookieJar
from celery import Celery
from celery.schedules import crontab

from db.cruds.client import SessionCRUD
from db.cruds.negotiation import AutoApplyConfigCRUD, FilterCRUD
from db.session import async_session

app = Celery("auto_apply", broker="redis://redis:6379/0")


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        crontab(hour=14, minute=00),
        run_auto_apply_tasks_sync.s(),
        name="auto-apply-daily",
    )


async def auto_apply_request(
    client_id: str,
    session: str,
    resume_id: str,
    max_applications: int,
    filter_query: dict,
):
    jar = CookieJar()
    jar.update_cookies({"client_id": client_id, "session": session})
    params = {"resume_id": resume_id, "max_applications": max_applications}

    async with ClientSession(cookie_jar=jar) as http_session:
        async with http_session.post(
            "http://hh-service:8000/auto_apply",
            params=params,
            json=filter_query,
        ) as response:
            result = await response.json()
    return result


async def get_auto_apply_tasks():
    async with async_session() as db_session:
        auto_apply_configs = await AutoApplyConfigCRUD.get_multi(
            db_session, {"enabled": True}
        )
        results = []
        for auto_apply_config in auto_apply_configs:
            client_id = auto_apply_config.user_id
            session = (
                await SessionCRUD.get_one(
                    db_session, {"id": auto_apply_config.session_id}
                )
            ).session
            resume_id = auto_apply_config.resume_id
            max_applications = auto_apply_config.max_applications
            query = (
                await FilterCRUD.get_one(
                    db_session, {"id": auto_apply_config.filter_id}
                )
            ).query
            results.append(
                await auto_apply_request(
                    client_id, session, resume_id, max_applications, query
                )
            )
    return results


async def run_auto_apply_tasks():
    results = await get_auto_apply_tasks()
    print(results)
    return results


@app.task
def run_auto_apply_tasks_sync():
    import asyncio

    asyncio.run(run_auto_apply_tasks())
