from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.common.sqla import TableNameMixin
from app.db.base import Base


class Filter(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)


class AutoApplyConfig(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.client_id", ondelete="CASCADE"),
        nullable=False,
    )
    resume_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("resume.resume_id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("session.id", ondelete="CASCADE"), nullable=False
    )
    filter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("filter.id", ondelete="CASCADE"), nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_applications: Mapped[int] = mapped_column(
        Integer, default=200, nullable=False
    )
