import asyncio
import uuid
import webbrowser
from typing import Dict
from urllib.parse import urlencode

from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_408_REQUEST_TIMEOUT

from app.db.session import get_db_session
from app.hh_integration.client.crud import client_crud
from app.hh_integration.client.schemas import (
    ClientBase,
    AuthorizedClient,
)
from app.hh_integration.common import HH_URLS


class OAuthHandler:
    def __init__(
        self, authorize_url: str, redirect_uri: str, timeout: int = 120
    ):
        self.authorize_url = authorize_url
        self.redirect_uri = redirect_uri
        self.timeout = timeout
        self._pending: Dict[str, asyncio.Future] = {}

    def build_auth_url(self, client_id: str, state: str) -> str:
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": state,
        }
        return f"{self.authorize_url}?{urlencode(params)}"

    async def authorize(self, client_id: str) -> str:
        state = uuid.uuid4().hex
        future = asyncio.get_event_loop().create_future()
        self._pending[state] = future

        auth_url = self.build_auth_url(client_id, state)
        webbrowser.open(auth_url)

        try:
            code = await asyncio.wait_for(future, timeout=self.timeout)
            return code
        except asyncio.TimeoutError:
            future.cancel()
            raise
        finally:
            await self._pending.pop(state, None)

    async def handle_callback(self, request: Request):
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not state or state not in self._pending:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Unknown state."
            )

        future = self._pending[state]
        if not future.done():
            future.set_result(code)

        return code


oauth_handler = OAuthHandler(
    authorize_url=HH_URLS.AUTHORIZE,
    # TODO: host, port, ...
    redirect_uri="http://localhost:8000/auth/callback",
)
oauth_router = APIRouter(prefix="/auth")


@oauth_router.get("/callback")
async def auth_callback(request: Request):
    return await oauth_handler.handle_callback(request)


@oauth_router.post("")
async def auth(client: ClientBase, db_session=Depends(get_db_session)):
    try:
        code = await oauth_handler.authorize(client.client_id)
        authorized_client = AuthorizedClient(
            client_id=client.client_id,
            client_secret=client.client_secret,
            code=code,
        )
        await client_crud.create(db_session, obj_in=authorized_client.__dict__)
        await db_session.commit()
        return {"code": code}
    except asyncio.CancelledError:
        raise HTTPException(status_code=HTTP_408_REQUEST_TIMEOUT)


if __name__ == "__main__":
    import os

    import uvicorn
    from fastapi import FastAPI

    host = os.getenv("API_HOST", "localhost")
    port = os.getenv("API_PORT", "8000")
    port = int(port)

    app = FastAPI(title="HHBOT")
    app.include_router(oauth_router)
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)

    async def main():
        await server.serve()

    asyncio.run(main())
