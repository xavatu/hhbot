from authlib.integrations.starlette_client import OAuth
from fastapi import Request, APIRouter, HTTPException, Depends
from starlette.responses import RedirectResponse

from hh_service.client import ClientSession, ClientToken
from hh_service.common import HHUrls

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

    token = await oauth.hh.authorize_access_token(
        request,
        client_id=request.session["client_creds"]["client_id"],
        client_secret=request.session["client_creds"]["client_secret"],
    )

    client_token = ClientToken(**token)
    code = request.query_params.get("code")

    request.session["client_session"] = ClientSession(
        client_id=request.session["client_creds"]["client_id"],
        client_secret=request.session["client_creds"]["client_secret"],
        code=code,
        token=client_token,
    ).model_dump()

    response = RedirectResponse(url="/docs")
    response.set_cookie(
        key="client_id",
        value=request.session["client_creds"]["client_id"],
        max_age=86400,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    del request.session["client_creds"]
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
            "redirect_uri": "http://localhost:8000/auth/callback"
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
