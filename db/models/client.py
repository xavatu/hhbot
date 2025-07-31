from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    TIMESTAMP,
    func,
    String,
    Integer,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDString
from .mixins import TableNameMixin


class Client(Base, TableNameMixin):
    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )


class Session(Base, TableNameMixin):
    id: Mapped[str] = mapped_column(UUIDString, primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("client.id", ondelete="CASCADE"),
        nullable=False,
    )
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=True)
    token: Mapped[dict] = mapped_column(JSONB, nullable=False)
    state: Mapped[str] = mapped_column(UUIDString, unique=True, nullable=True)
    status: Mapped[str] = mapped_column(
        String, default="pending", nullable=False
    )
    encoded: Mapped[str] = mapped_column(String, nullable=True)
    mode: Mapped[str] = mapped_column(String, default="web", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
