from datetime import datetime
from typing import List

from sqlalchemy import (
    BigInteger,
    Integer,
    Text,
    ForeignKey,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TableNameMixin
from .negotiation import AutoApplyConfig
from .resume import Resume


class User(Base, TableNameMixin):
    client_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    sessions: Mapped[List["Session"]] = relationship(
        cascade="all, delete-orphan"
    )
    resumes: Mapped[List["Resume"]] = relationship(cascade="all, delete-orphan")
    auto_apply_configs: Mapped[List["AutoApplyConfig"]] = relationship(
        cascade="all, delete-orphan"
    )


class Session(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.client_id", ondelete="CASCADE"),
        nullable=False,
    )
    session: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
