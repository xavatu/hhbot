from typing import Dict

import aiohttp
from fastapi import APIRouter, Depends

from hh_service.common import HHUrls
from shared_utils.http_session import get_http_session
from shared_utils.query_extra import get_extra_params, query_extra

resume_router = APIRouter(prefix="/resumes", tags=["resume"])

from hh_service.client.oauth import ClientSession, get_client_session


@resume_router.get("/mine")
async def get_resumes(
    client_session: ClientSession = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    result = await http_session.get(
        HHUrls.RESUMES + "/mine",
        headers={
            "Authorization": f"Bearer {client_session.token.access_token}"
        },
    )
    if not result.ok:
        result.raise_for_status()
    result_json = await result.json()
    return result_json


@resume_router.get("/{resume_id}/similar_vacancies")
@query_extra()
async def get_similar_vacancies(
    resume_id: str,
    extra_params: Dict = Depends(get_extra_params),
    client_session: ClientSession = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    result = await http_session.get(
        HHUrls.RESUMES + f"/{resume_id}/similar_vacancies",
        params=extra_params,
        headers={
            "Authorization": f"Bearer {client_session.token.access_token}"
        },
    )
    if not result.ok:
        result.raise_for_status()
    result_json = await result.json()
    return result_json
