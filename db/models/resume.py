from sqlalchemy import (
    String,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import TableNameMixin


class Resume(Base, TableNameMixin):
    resume_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("user.client_id", ondelete="CASCADE"),
        nullable=False,
    )
