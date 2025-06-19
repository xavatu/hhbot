from sqlalchemy import (
    BigInteger,
    String,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import TableNameMixin


class Resume(Base, TableNameMixin):
    resume_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.client_id", ondelete="CASCADE"),
        nullable=False,
    )
