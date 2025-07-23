from __future__ import annotations

import asyncio
import json
import typing
import uuid
from base64 import b64decode, b64encode

import itsdangerous
import sqlalchemy.exc
from itsdangerous.exc import BadSignature
from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from db.models import Session
from db.session import async_session
from fabric.cruds.base import CRUDBase

SessionCRUD = CRUDBase(Session)


class SessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        secret_key: str | Secret,
        session_cookie: str = "session",
        max_age: int | None = 14 * 24 * 60 * 60,  # 14 days, in seconds
        path: str = "/",
        same_site: typing.Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
        domain: str | None = None,
    ) -> None:
        self.app = app
        self.signer = itsdangerous.TimestampSigner(str(secret_key))
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.path = path
        self.security_flags = "httponly; samesite=" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"
        if domain is not None:
            self.security_flags += f"; domain={domain}"

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True

        if self.session_cookie in connection.cookies:
            data = connection.cookies[self.session_cookie].encode("utf-8")
            try:
                data = self.signer.unsign(data, max_age=self.max_age)
                scope["session"] = json.loads(b64decode(data))
                initial_session_was_empty = False
            except BadSignature:
                scope["session"] = {}
        else:
            scope["session"] = {}

        if "session_id" not in scope["session"]:
            scope["session"]["session_id"] = str(uuid.uuid4())

        session_snapshot = dict(scope["session"])

        async def persist_session_to_db(data, encoded_data):
            session_id = data["session_id"]
            client_id = data["client_id"]
            async with async_session() as db_session:
                try:
                    session_obj = await SessionCRUD.get_one(
                        db_session, dict(id=session_id)
                    )
                except sqlalchemy.exc.NoResultFound:
                    raise
                else:
                    session_obj.token = data.get("token", {})
                    session_obj.encoded = encoded_data
                await db_session.commit()

        async def send_wrapper(message: Message) -> None:
            session_changed = scope["session"] != session_snapshot
            if message["type"] == "http.response.start":
                if scope["session"]:
                    # We have session data to persist.
                    data = b64encode(
                        json.dumps(scope["session"]).encode("utf-8")
                    )
                    data = self.signer.sign(data)
                    encoded_data = data.decode("utf-8")
                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(
                        session_cookie=self.session_cookie,
                        data=encoded_data,
                        path=self.path,
                        max_age=(
                            f"Max-Age={self.max_age}; " if self.max_age else ""
                        ),
                        security_flags=self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
                    if session_changed:
                        asyncio.create_task(
                            persist_session_to_db(
                                data=dict(scope["session"]),
                                encoded_data=encoded_data,
                            )
                        )
                elif not initial_session_was_empty:
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(
                        session_cookie=self.session_cookie,
                        data="null",
                        path=self.path,
                        expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                        security_flags=self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
                    if session_changed:
                        asyncio.create_task(persist_session_to_db({}))

            await send(message)

        await self.app(scope, receive, send_wrapper)
