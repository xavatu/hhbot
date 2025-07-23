import requests

from db.models import Session, Filter
from .config import celery_app, sync_session


def auto_apply_request(
    session: str,
    resume_id: str,
    max_applications: int,
    similar_vacancies: bool,
    message: str,
    filter_query: dict,
):
    cookies = {"session": session}
    params = {
        "resume_id": resume_id,
        "max_applications": max_applications,
        "similar_vacancies": str(similar_vacancies),
        "message": message,
    }

    response = requests.post(
        "http://hh-service:8000/auto_apply",
        params=params,
        json=filter_query,
        cookies=cookies,
    )
    response.raise_for_status()
    return response.json()


def run_single_auto_apply_task(
    session_id,
    resume_id,
    filter_id,
    max_applications,
    similar_vacancies,
    message,
):
    with sync_session() as db_session:
        session_obj = db_session.get(Session, session_id)
        filter_obj = db_session.get(Filter, filter_id)
        session_val = session_obj.encoded
        query = filter_obj.query

        result = auto_apply_request(
            session_val,
            resume_id,
            max_applications,
            similar_vacancies,
            message,
            query,
        )
    print(result)
    return result


@celery_app.task(name="tasks.run_auto_apply_task_sync")
def run_auto_apply_task_sync(
    session_id,
    resume_id,
    filter_id,
    max_applications,
    similar_vacancies,
    message,
):
    return run_single_auto_apply_task(
        session_id,
        resume_id,
        filter_id,
        max_applications,
        similar_vacancies,
        message,
    )
