import uuid

import sqlalchemy
from authlib.integrations.starlette_client import OAuth
from fastapi import Request, APIRouter, Depends, HTTPException
from starlette.responses import RedirectResponse

from db.models import Client, Session
from db.session import async_session
from hh_service.client.sessions import SessionCRUD
from hh_service.common.urls import HHUrls
from hh_service.config import (
    CLIENT_ID,
    CLIENT_SECRET,
)

oauth = OAuth()
oauth.register(
    name="hh",
    authorize_url=HHUrls.AUTHORIZE,
    access_token_url=HHUrls.TOKEN,
    refresh_token_url=HHUrls.TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        "token_endpoint_auth_method": "client_secret_post",
    },
)
oauth_router = APIRouter(prefix="/auth", tags=["auth"])


async def get_client_session(request: Request):
    if not request.session.get("token", None):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return request.session


@oauth_router.get("/callback")
async def auth_callback(request: Request):
    token = await oauth.hh.authorize_access_token(
        request,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    session_id = request.session["session_id"]
    state = request.session["state"]
    del request.session["state"]

    request.session["token"] = token
    request.session["status"] = "active"

    async with async_session() as db_session:
        await SessionCRUD.update(
            db_session,
            filter_dict=dict(id=session_id),
            update_dict=dict(token=token, state=None, status="active"),
            is_patch=False,
        )
        await db_session.commit()

    return RedirectResponse(url="/docs")


@oauth_router.get("")
async def login(
    request: Request,
    mode: str = "web",
):
    session_id = str(uuid.uuid4())
    state = str(uuid.uuid4())
    request.session["session_id"] = session_id
    request.session["state"] = state
    request.session["client_id"] = CLIENT_ID
    request.session["status"] = "pending"

    async with async_session() as db_session:
        try:
            await db_session.get_one(Client, CLIENT_ID)
        except sqlalchemy.exc.NoResultFound:
            user = Client(id=CLIENT_ID)
            db_session.add(user)
        session = Session(
            id=session_id,
            client_id=CLIENT_ID,
            token={},
            state=state,
            status="pending",
            mode=mode,
        )
        db_session.add(session)
        await db_session.commit()

    redirect_uri = request.url_for("auth_callback")
    return await oauth.hh.authorize_redirect(request, redirect_uri, state=state)


@oauth_router.get("/session")
async def get_session(
    session=Depends(get_client_session),
):
    return session
