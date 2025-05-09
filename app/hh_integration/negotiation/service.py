import aiohttp
from fastapi import APIRouter, Depends

from app.common.http_session import get_http_session
from app.hh_integration.client.oauth import get_client_session
from app.hh_integration.client.schemas import ClientSession
from app.hh_integration.common import HHUrls
from app.hh_integration.negotiation.schemas import Negotiation

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
