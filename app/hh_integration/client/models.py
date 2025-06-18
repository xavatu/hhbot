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

from app.common.sqla import TableNameMixin
from app.db.base import Base
from app.hh_integration.negotiation.models import AutoApplyConfig
from app.hh_integration.resume.models import Resume


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
        ForeignKey("users.client_id", ondelete="CASCADE"),
        nullable=False,
    )
    session: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
