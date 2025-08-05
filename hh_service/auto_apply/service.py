import asyncio
import traceback
from functools import partial
from typing import Optional, AsyncIterator, Callable, Awaitable, Dict

import aiohttp
from aiohttp import ClientResponseError
from fastapi import APIRouter, Depends

from hh_service.client.oauth import get_client_session
from hh_service.common.async_pagination import (
    AsyncList,
    AsyncItemPaged,
    async_chunks,
)
from hh_service.common.http_session import get_http_session
from hh_service.common.logger import logger
from hh_service.negotiation import Negotiation
from hh_service.negotiation.service import apply_vacancy, get_negotiations
from hh_service.resume.service import get_similar_vacancies
from hh_service.vacancies.service import (
    get_vacancies,
    get_vacancies_by_saved_search,
)

auto_apply_router = APIRouter(prefix="/auto_apply", tags=["auto_apply"])


async def get_next(
    continuation_token: Optional[str],
    *,
    get_next_page: Callable[..., Awaitable[dict]],
    **kwargs,
) -> dict:
    page = int(continuation_token) if continuation_token is not None else 0
    return await get_next_page(page=page, **kwargs)


async def extract_data(
    response: dict,
) -> tuple[Optional[str], AsyncIterator[dict]]:
    page = response.get("page", 0)
    pages = response.get("pages", 1)
    items = response.get("items", [])
    next_token = page + 1 if (page + 1) < pages else None
    return next_token, AsyncList(items)


async def get_already_applied(
    client_session,
    http_session: aiohttp.ClientSession,
    resume_id: str = None,
) -> set[str]:
    get_next_negotiations = partial(
        get_next,
        per_page=200,
        get_next_page=get_negotiations,
        client_session=client_session,
        http_session=http_session,
    )
    sequence = AsyncItemPaged(get_next_negotiations, extract_data)
    negotiations = [item async for item in sequence]
    if resume_id is None:
        return set([item["id"] for item in negotiations])
    return set(
        [
            item["id"]
            for item in negotiations
            if item["resume"] and item["resume"]["id"] == resume_id
        ]
    )


async def auto_apply(
    get_next_vacancies,
    resume_id: str,
    max_applications: int = 200,
    message: str = "",
    client_session=Depends(),
    http_session: aiohttp.ClientSession = Depends(),
) -> int:
    already_applied = await get_already_applied(
        client_session, http_session, resume_id
    )
    sequence = AsyncItemPaged(get_next_vacancies, extract_data)
    sequence_chunks = async_chunks(sequence, max_applications)
    success_count = 0
    tail = []
    limit_exceeded = False

    while success_count < max_applications and not limit_exceeded:
        need = max_applications - success_count
        vacancies = (
            tail
            if len(tail) >= need
            else tail + await anext(sequence_chunks, [])
        )
        if not vacancies:
            break

        filtered = [
            vacancy
            for vacancy in vacancies
            if not vacancy["has_test"] and vacancy["id"] not in already_applied
        ]
        logger.debug(
            f"{success_count=} {need=} {len(vacancies)=} {len(filtered)=}"
        )
        if not filtered:
            continue

        head, tail = filtered[:need], filtered[need:]
        negotiations = [
            Negotiation(
                resume_id=resume_id, vacancy_id=v["id"], message=message
            )
            for v in head
        ]
        results = await asyncio.gather(
            *(
                apply_vacancy(negotiation, client_session, http_session)
                for negotiation in negotiations
            ),
            return_exceptions=True,
        )
        for exception in filter(lambda x: isinstance(x, Exception), results):
            payload_json = getattr(exception, "payload_json", {})
            try:
                raise exception
            except ClientResponseError:
                logger.error(traceback.format_exc(), payload_json=payload_json)
            error_type = payload_json.get("errors", [{}])[0].get("value", None)
            if error_type == "already_applied":
                ...
            if error_type == "limit_exceeded":
                limit_exceeded = True
                break

        applied = sum(1 for res in results if not isinstance(res, Exception))
        success_count += applied

    return success_count


@auto_apply_router.post("")
async def run_auto_apply(
    resume_id: str,
    extra_params: dict,
    max_applications: Optional[int] = 200,
    similar_vacancies: bool = True,
    message: str = "",
    client_session: Dict = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    get_vacancies_func = (
        partial(get_similar_vacancies, resume_id=resume_id)
        if similar_vacancies
        else partial(get_vacancies)
    )
    get_next_vacancies = partial(
        get_next,
        get_next_page=get_vacancies_func,
        extra_params=extra_params,
        client_session=client_session,
        http_session=http_session,
    )
    success_count = await auto_apply(
        get_next_vacancies=get_next_vacancies,
        resume_id=resume_id,
        max_applications=max_applications,
        message=message,
        client_session=client_session,
        http_session=http_session,
    )
    return {
        "detail": "Auto apply completed",
        "resume_id": resume_id,
        "success_count": success_count,
    }


@auto_apply_router.post("/by_saved_search")
async def run_auto_apply_by_saved_search(
    saved_search_id: str,
    resume_id: str,
    max_applications: Optional[int] = 200,
    message: str = "",
    client_session: Dict = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    get_vacancies_func = partial(
        get_vacancies_by_saved_search,
        saved_search_id=saved_search_id,
    )
    get_next_vacancies = partial(
        get_next,
        get_next_page=get_vacancies_func,
        client_session=client_session,
        http_session=http_session,
    )
    success_count = await auto_apply(
        get_next_vacancies=get_next_vacancies,
        resume_id=resume_id,
        max_applications=max_applications,
        message=message,
        client_session=client_session,
        http_session=http_session,
    )
    return {
        "detail": "Auto apply completed",
        "resume_id": resume_id,
        "success_count": success_count,
    }
