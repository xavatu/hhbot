import datetime

from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    model_config = ConfigDict(frozen=True)
    client_id: str
    client_secret: str


class AuthorizedClient(ClientBase):
    code: str


class ClientToken(BaseModel):
    model_config = ConfigDict(frozen=True)
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int
    expires_at: int

    @property
    def is_expired(self):
        return self.expires_at < int(
            datetime.datetime.now(datetime.UTC).timestamp()
        )


class ClientSession(AuthorizedClient):
    token: ClientToken

    @property
    def is_expired(self) -> bool:
        return self.token.is_expired
