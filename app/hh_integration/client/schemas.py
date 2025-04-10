from dataclasses import dataclass, field
from datetime import datetime, timezone

import pydantic.dataclasses


@dataclass(frozen=True)
class ClientBase:
    client_id: str
    client_secret: str


@dataclass(frozen=True)
class AuthorizedClient(ClientBase):
    code: str


@dataclass(frozen=True)
class ClientToken:
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_expired(self) -> bool:
        elapsed_time = (
            datetime.now(timezone.utc) - self.created_at
        ).total_seconds()
        return self.expires_in - elapsed_time < 0


@dataclass(frozen=True)
class ClientSession(AuthorizedClient):
    token: ClientToken

    @property
    def is_expired(self) -> bool:
        return self.token.is_expired


@pydantic.dataclasses.dataclass(frozen=True)
class AuthorizedClientSchema(AuthorizedClient):
    ...


@pydantic.dataclasses.dataclass(frozen=True)
class ClientTokenSchema(ClientToken):
    ...
