import aiohttp
from fastapi import APIRouter, Depends

from app.common.http_session import get_http_session
from app.hh_integration.client.oauth import get_client_session
from app.hh_integration.client.schemas import ClientSession
from app.hh_integration.common import HHUrls

resume_router = APIRouter(prefix="/resumes", tags=["resume"])


@resume_router.get("")
async def get_resumes(
    client_session: ClientSession = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    result = await http_session.get(
        HHUrls.RESUMES,
        headers={
            "Authorization": f"Bearer {client_session.token.access_token}"
        },
    )
    if not result.ok:
        result.raise_for_status()
    result_json = await result.json()
    return result_json
