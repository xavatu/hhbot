from celery import Celery
from celery.schedules import crontab

from db.cruds.negotiation import AutoApplyConfigCRUD
from db.session import async_session

app = Celery()


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(crontab(hour=11, minute=20), get_auto_apply_tasks)


@app.task
async def get_auto_apply_tasks():
    async with async_session() as session:
        result = await AutoApplyConfigCRUD.get_multi(session, {})
        print(result)
        return result


if __name__ == "__main__":
    import asyncio

    asyncio.run(get_auto_apply_tasks())
