from sqlalchemy import (
    Integer,
    String,
    Boolean,
    ForeignKey,
    UUID,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, CronSchedule
from .mixins import TableNameMixin


class Filter(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    query: Mapped[dict] = mapped_column(JSONB, nullable=False)


class AutoApplyConfig(Base, TableNameMixin):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    client_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("client.id", ondelete="CASCADE"),
        nullable=False,
    )
    resume_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[int] = mapped_column(
        UUID, ForeignKey("session.id", ondelete="CASCADE"), nullable=False
    )
    filter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("filter.id", ondelete="CASCADE"), nullable=True
    )
    saved_search_id: Mapped[str] = mapped_column(String, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_applications: Mapped[int] = mapped_column(
        Integer, default=200, nullable=False
    )
    similar_vacancies: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    cron_schedule: Mapped[str] = mapped_column(CronSchedule, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=True)
