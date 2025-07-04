import json
from base64 import b64encode

import itsdangerous
import sqlalchemy.exc
from authlib.integrations.starlette_client import OAuth
from fastapi import Request, APIRouter, HTTPException, Depends
from starlette.datastructures import Secret
from starlette.responses import RedirectResponse

from db.models import Session, User
from db.session import async_session
from hh_service.client import ClientSession, ClientToken
from hh_service.common.urls import HHUrls
from hh_service.config import port, secret_key, session_max_age

oauth = OAuth()
oauth_router = APIRouter(prefix="/auth", tags=["auth"])


def get_client_session(request: Request):
    if "client_session" not in request.session:
        raise HTTPException(status_code=401, detail="Unauthorized")

    client_session = ClientSession(**request.session["client_session"])

    if client_session.token.is_expired:
        raise HTTPException(status_code=401, detail="Session expired")

    return client_session


@oauth_router.get("/callback")
async def auth_callback(request: Request):
    if "client_creds" not in request.session:
        raise HTTPException(
            status_code=400, detail="Client credentials not found"
        )

    client_id = request.session["client_creds"]["client_id"]
    client_secret = request.session["client_creds"]["client_secret"]

    token = await oauth.hh.authorize_access_token(
        request,
        client_id=client_id,
        client_secret=client_secret,
    )

    client_token = ClientToken(**token)
    code = request.query_params.get("code")

    client_session_obj = ClientSession(
        client_id=client_id,
        client_secret=client_secret,
        code=code,
        token=client_token,
    )
    request.session["client_session"] = client_session_obj.model_dump()
    del request.session["client_creds"]

    session_raw = request.session
    session_encoded_bytes = b64encode(json.dumps(session_raw).encode("utf-8"))
    signer = itsdangerous.TimestampSigner(str(Secret(secret_key)))
    session_encoded = signer.sign(session_encoded_bytes).decode("utf-8")

    client_session = ClientSession.model_validate(session_raw["client_session"])
    session = Session(user_id=client_session.client_id, session=session_encoded)
    async with async_session() as db_session:
        try:
            await db_session.get_one(User, session.user_id)
        except sqlalchemy.exc.NoResultFound:
            user = User(client_id=session.user_id)
            db_session.add(user)

        db_session.add(session)
        await db_session.commit()

    response = RedirectResponse(url="/docs")
    response.set_cookie(
        "session",
        value=session_encoded,
        max_age=session_max_age,
        path="/",
        httponly=True,
        samesite="lax",
    )
    return response


@oauth_router.get("")
async def login(request: Request, client_id: str, client_secret: str):
    request.session["client_creds"] = {
        "client_id": client_id,
        "client_secret": client_secret,
    }

    oauth.register(
        name="hh",
        authorize_url=HHUrls.AUTHORIZE,
        authorize_params={
            "redirect_uri": f"http://localhost:{port}/auth/callback"
        },
        access_token_url=HHUrls.TOKEN,
        refresh_token_url=HHUrls.TOKEN,
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={
            "token_endpoint_auth_method": "client_secret_post",
        },
    )

    redirect_uri = request.url_for("auth_callback")
    return await oauth.hh.authorize_redirect(request, redirect_uri)


@oauth_router.get("/session")
async def get_session(
    client_session: ClientSession = Depends(get_client_session),
):
    return client_session
