from sqlalchemy import (
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.common.sqla import TableNameMixin
from app.db.base import Base


class Client(Base, TableNameMixin):
    client_id: Mapped[str] = mapped_column(String, primary_key=True)
    client_secret: Mapped[str]
    code: Mapped[str]
