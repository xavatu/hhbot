import asyncio

import aiohttp
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app.common.cache import memoize
from app.config import cache
from app.hh_integration.common import HH_PARAMS, HH_URLS
from app.hh_integration.client.schemas import (
    ClientBase,
    ClientToken,
    ClientSession,
    AuthorizedClient,
)


class AuthorizationService:
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

    # @staticmethod
    # async def authorize(
    #     client: ClientBase, http_session: aiohttp.ClientSession
    # ) -> AuthorizedClient:
    #     result = await http_session.post(
    #         HH_URLS.AUTHORIZE,
    #         data={"client_id": client.client_id, "response_type": "code"},
    #     )
    #     print(await result.text())
    #     if not result.ok:
    #         result.raise_for_status()
    #     result_json = await result.json()
    #     print(result_json)
    #     return None

    @staticmethod
    async def authorize(
        client: ClientBase, http_session: aiohttp.ClientSession
    ) -> AuthorizedClient:
        params = {
            "client_id": client.client_id,
            "response_type": "code",
        }
        auth_url = f"{HH_URLS.AUTHORIZE}?{urlencode(params)}"
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(auth_url)
        await asyncio.sleep(30)

    @staticmethod
    @memoize(cache, expiration=HH_PARAMS.ACCESS_TOKEN_TTL)
    async def get_session(
        authorized_client: AuthorizedClient, http_session
    ) -> ClientSession:
        token = await AuthorizationService._get_access_token(
            authorized_client, http_session
        )
        return ClientSession(**authorized_client.__dict__, token=token)

    @staticmethod
    async def refresh_session(
        client_session: ClientSession, http_session
    ) -> ClientSession:
        new_token = await AuthorizationService._refresh_token(
            client_session, http_session
        )
        return ClientSession(
            client_id=client_session.client_id,
            client_secret=client_session.client_secret,
            code=client_session.code,
            token=new_token,
        )
