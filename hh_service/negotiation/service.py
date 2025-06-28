import aiohttp
from fastapi import APIRouter, Depends

from hh_service.client.oauth import ClientSession, get_client_session
from hh_service.common import HHUrls
from hh_service.negotiation import Negotiation
from shared_utils.http_session import get_http_session

negotiation_router = APIRouter(prefix="/negotiations", tags=["negotiation"])


@negotiation_router.post("")
async def apply_vacancy(
    negotiation: Negotiation,
    client_session: ClientSession = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    result = await http_session.post(
        HHUrls.NEGOTIATIONS,
        data=negotiation.model_dump(exclude_none=True),
        headers={
            "Authorization": f"Bearer {client_session.token.access_token}"
        },
    )
    if not result.ok:
        result.raise_for_status()
    result_text = await result.text()
    return {"text": result_text}
