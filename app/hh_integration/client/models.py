from datetime import datetime
from typing import List

from sqlalchemy import (
    Identity,
    String,
    ForeignKey,
    DateTime,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.common.sqla import TableNameMixin

# from app.hh_integration.client.schemas import ClientToken


class Client(Base, TableNameMixin):
    client_id: Mapped[str] = mapped_column(String, primary_key=True)
    client_secret: Mapped[str]
    code: Mapped[str]

    # tokens: Mapped[List[ClientToken]] = relationship(
    #     "Token", back_populates="client", cascade="all"
    # )


# class Token(Base, TableNameMixin):
#     token_id: Mapped[int] = mapped_column(Identity(), primary_key=True)
#     access_token: Mapped[str]
#     token_type: Mapped[str]
#     refresh_token: Mapped[str]
#     expires_in: Mapped[int]
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
#     )
#
#     client_id: Mapped[str] = mapped_column(
#         String, ForeignKey("client.client_id")
#     )
#     client: Mapped["Client"] = relationship("Client", back_populates="tokens")
