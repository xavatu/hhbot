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
