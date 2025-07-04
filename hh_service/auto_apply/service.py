import asyncio
from functools import partial
from itertools import islice  # noqa
from typing import Optional, AsyncIterator, Callable, Awaitable

import aiohttp
from fastapi import APIRouter, Depends

from hh_service.client.oauth import ClientSession, get_client_session
from hh_service.common.async_pagination import (
    AsyncList,
    AsyncItemPaged,
    async_chunks,
)
from hh_service.common.http_session import get_http_session
from hh_service.negotiation import Negotiation
from hh_service.negotiation.service import apply_vacancy, get_negotiations
from hh_service.resume.service import get_similar_vacancies
from hh_service.vacancies.service import get_vacancies

auto_apply_router = APIRouter(prefix="/auto_apply", tags=["auto_apply"])
default_negotiation_message = (
    "Добрый день! Вакансия показалась мне очень интересной. "
    "Если Вас заинтересует моя кандидатура, пожалуйста, свяжитесь со мной в Telegram: @xavatu."
)


def make_negotiation(
    resume_id, vacancy_id, message=default_negotiation_message
):
    return Negotiation(
        resume_id=resume_id, vacancy_id=vacancy_id, message=message
    )


async def get_next(
    continuation_token: Optional[str],
    *,
    coroutine: Callable[..., Awaitable[dict]],
    **kwargs,
) -> dict:
    page = int(continuation_token) if continuation_token is not None else 0
    return await coroutine(page=page, **kwargs)


async def extract_data(
    response: dict,
) -> tuple[Optional[str], AsyncIterator[dict]]:
    page = response.get("page", 0)
    pages = response.get("pages", 1)
    items = response.get("items", [])
    next_token = page + 1 if (page + 1) < pages else None
    return next_token, AsyncList(items)


async def get_already_applied(
    client_session: ClientSession,
    http_session: aiohttp.ClientSession,
) -> set[str]:
    get_next_negotiations = partial(
        get_next,
        per_page=200,
        coroutine=get_negotiations,
        client_session=client_session,
        http_session=http_session,
    )
    sequence = AsyncItemPaged(get_next_negotiations, extract_data)
    return set([item["id"] async for item in sequence])


async def auto_apply(
    resume_id: str,
    extra_params: dict,
    client_session: ClientSession,
    http_session: aiohttp.ClientSession,
    max_applications: int = 200,
    similar_vacancies: bool = True,
) -> int:
    already_applied = await get_already_applied(client_session, http_session)
    get_vacancies_func = (
        partial(get_similar_vacancies, resume_id=resume_id)
        if similar_vacancies
        else partial(get_vacancies)
    )
    get_next_vacancies = partial(
        get_next,
        coroutine=get_vacancies_func,
        extra_params=extra_params,
        client_session=client_session,
        http_session=http_session,
    )
    sequence = AsyncItemPaged(get_next_vacancies, extract_data)
    sequence_chunks = async_chunks(sequence, max_applications)
    success_count = 0
    tail = []

    while success_count < max_applications:
        need = max_applications - success_count
        vacancies = (
            tail
            if len(tail) >= need
            else tail + await anext(sequence_chunks, [])
        )

        if not vacancies:
            break

        filtered = [
            x
            for x in vacancies
            if not x["has_test"] and x["id"] not in already_applied
        ]
        print(f"{success_count=} {need=} {len(vacancies)=} {len(filtered)=}")

        if not filtered:
            continue

        head, tail = filtered[:need], filtered[need:]
        negotiations = [make_negotiation(resume_id, v["id"]) for v in head]

        results = await asyncio.gather(
            *[
                apply_vacancy(n, client_session, http_session)
                for n in negotiations
            ],
            return_exceptions=True,
        )
        for exception in filter(lambda x: isinstance(x, Exception), results):
            print(exception.__dict__)
        applied = sum(1 for res in results if not isinstance(res, Exception))
        success_count += applied

    return success_count


@auto_apply_router.post("")
async def run_auto_apply(
    resume_id: str,
    extra_params: dict,
    max_applications: Optional[int] = 200,
    similar_vacancies: bool = True,
    client_session: ClientSession = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    success_count = await auto_apply(
        resume_id=resume_id,
        extra_params=extra_params,
        client_session=client_session,
        http_session=http_session,
        max_applications=max_applications,
        similar_vacancies=similar_vacancies,
    )
    return {
        "detail": "Auto apply completed",
        "resume_id": resume_id,
        "success_count": success_count,
    }
