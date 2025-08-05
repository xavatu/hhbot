import requests

from db.models import Session, Filter
from .config import celery_app, sync_session


def auto_apply_request(
    session: str,
    resume_id: str,
    max_applications: int,
    message: str,
    similar_vacancies: bool,
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


def auto_apply_by_saved_search_request(
    session: str,
    resume_id: str,
    max_applications: int,
    message: str,
    saved_search_id: str,
):
    cookies = {"session": session}
    params = {
        "resume_id": resume_id,
        "saved_search_id": saved_search_id,
        "max_applications": max_applications,
        "message": message,
    }

    response = requests.post(
        "http://hh-service:8000/auto_apply/by_saved_search",
        params=params,
        cookies=cookies,
    )
    response.raise_for_status()
    return response.json()


def run_single_auto_apply_task(
    session_id,
    resume_id,
    filter_id,
    saved_search_id,
    max_applications,
    similar_vacancies,
    message,
):
    with sync_session() as db_session:
        session_obj = db_session.get(Session, session_id)
        session_val = session_obj.encoded

        if saved_search_id:
            result = auto_apply_by_saved_search_request(
                session_val,
                resume_id,
                max_applications,
                message,
                saved_search_id,
            )
        else:
            filter_obj = db_session.get(Filter, filter_id)
            query = filter_obj.query

            result = auto_apply_request(
                session_val,
                resume_id,
                max_applications,
                message,
                similar_vacancies,
                query,
            )
    print(result)
    return result


@celery_app.task(name="tasks.run_auto_apply_task_sync")
def run_auto_apply_task_sync(
    session_id,
    resume_id,
    filter_id,
    saved_search_id,
    max_applications,
    similar_vacancies,
    message,
):
    return run_single_auto_apply_task(
        session_id,
        resume_id,
        filter_id,
        saved_search_id,
        max_applications,
        similar_vacancies,
        message,
    )
