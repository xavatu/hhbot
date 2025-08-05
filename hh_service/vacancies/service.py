from typing import Dict

import aiohttp
from fastapi import APIRouter, Depends

from hh_service.common.http_session import get_http_session
from hh_service.common.query_extra import get_extra_params, query_extra
from hh_service.common.urls import HHUrls

vacancy_router = APIRouter(prefix="/vacancies", tags=["vacancy"])

from hh_service.client.oauth import get_client_session


@vacancy_router.get("")
@query_extra()
async def get_vacancies(
    page: int = 0,
    per_page: int = 100,
    extra_params: Dict = Depends(get_extra_params),
    client_session: Dict = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    extra_params.update(page=page, per_page=per_page)
    result = await http_session.get(
        HHUrls.VACANCIES,
        params=extra_params,
        headers={
            "Authorization": f"Bearer {client_session["token"]["access_token"]}"
        },
    )
    if not result.ok:
        result.raise_for_status()
    result_json = await result.json()
    return result_json


@vacancy_router.get("/saved_searches")
async def get_saved_searches(
    page: int = 0,
    per_page: int = 10,
    client_session: Dict = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    result = await http_session.get(
        HHUrls.SAVED_SEARCHES + "/vacancies",
        params=dict(page=page, per_page=per_page),
        headers={
            "Authorization": f"Bearer {client_session["token"]["access_token"]}"
        },
    )
    if not result.ok:
        result.raise_for_status()
    result_json = await result.json()
    return result_json


@vacancy_router.get("/saved_searches/{id}")
async def get_saved_search(
    id: str,
    client_session: Dict = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    result = await http_session.get(
        HHUrls.SAVED_SEARCHES + f"/vacancies/{id}",
        headers={
            "Authorization": f"Bearer {client_session["token"]["access_token"]}"
        },
    )
    if not result.ok:
        result.raise_for_status()
    result_json = await result.json()
    return result_json


@vacancy_router.get("/by_saved_search")
async def get_vacancies_by_saved_search(
    saved_search_id: str,
    page: int = 0,
    per_page: int = 100,
    client_session: Dict = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    saved_search = await get_saved_search(
        saved_search_id, client_session, http_session
    )
    search_url = saved_search["items"]["url"]
    result = await http_session.get(
        search_url,
        params=dict(page=page, per_page=per_page),
        headers={
            "Authorization": f"Bearer {client_session["token"]["access_token"]}"
        },
    )
    if not result.ok:
        result.raise_for_status()
    result_json = await result.json()
    return result_json
