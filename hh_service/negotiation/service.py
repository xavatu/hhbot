from typing import Dict

import aiohttp
from aiohttp import ClientResponseError
from fastapi import APIRouter, Depends

from hh_service.client.oauth import get_client_session
from hh_service.common.http_session import get_http_session
from hh_service.common.urls import HHUrls
from hh_service.negotiation import Negotiation

negotiation_router = APIRouter(prefix="/negotiations", tags=["negotiation"])


@negotiation_router.get("")
async def get_negotiations(
    page: int = 0,
    per_page: int = 100,
    client_session: Dict = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    result = await http_session.get(
        HHUrls.NEGOTIATIONS,
        params=dict(page=page, per_page=per_page),
        headers={
            "Authorization": f"Bearer {client_session["token"]["access_token"]}"
        },
    )
    if not result.ok:
        result.raise_for_status()
    result_json = await result.json()
    return result_json


@negotiation_router.post("")
async def apply_vacancy(
    negotiation: Negotiation,
    client_session: Dict = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    result = await http_session.post(
        HHUrls.NEGOTIATIONS,
        data=negotiation.model_dump(exclude_none=True),
        headers={
            "Authorization": f"Bearer {client_session["token"]["access_token"]}"
        },
    )
    if not result.ok:
        try:
            payload_json = await result.json()
        except Exception as e:
            raise e
        try:
            result.raise_for_status()
        except ClientResponseError as e:
            e.payload_json = payload_json
            raise e
    result_text = await result.text()
    return {"text": result_text}
