from app.common.cache import memoize
from app.config import cache
from app.hh_integration.client.schemas import (
    ClientToken,
    ClientSession,
    AuthorizedClient,
)
from app.hh_integration.common import HH_PARAMS, HH_URLS


class SessionService:
    @staticmethod
    async def _get_access_token(
        authorized_client: AuthorizedClient, http_session
    ) -> ClientToken:
        result = await http_session.post(
            HH_URLS.TOKEN,
            data={
                **authorized_client.__dict__,
                "grant_type": "authorization_code",
            },
        )
        if not result.ok:
            result.raise_for_status()
        result_json = await result.json()
        return ClientToken(**result_json)

    @staticmethod
    async def _refresh_token(
        client_session: ClientSession, http_session
    ) -> ClientToken:
        result = await http_session.post(
            HH_URLS.TOKEN,
            data={
                "refresh_token": client_session.token.refresh_token,
                "client_id": client_session.client_id,
                "client_secret": client_session.client_secret,
                "grant_type": "refresh_token",
            },
        )
        if not result.ok:
            result.raise_for_status()
        result_json = await result.json()
        return ClientToken(**result_json)

    @staticmethod
    @memoize(cache, expiration=HH_PARAMS.ACCESS_TOKEN_TTL)
    async def get_session(
        authorized_client: AuthorizedClient, http_session
    ) -> ClientSession:
        token = await SessionService._get_access_token(
            authorized_client, http_session
        )
        return ClientSession(**authorized_client.__dict__, token=token)

    @staticmethod
    async def refresh_session(
        client_session: ClientSession, http_session
    ) -> ClientSession:
        new_token = await SessionService._refresh_token(
            client_session, http_session
        )
        return ClientSession(
            client_id=client_session.client_id,
            client_secret=client_session.client_secret,
            code=client_session.code,
            token=new_token,
        )
