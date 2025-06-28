import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime.datetime: DateTime(timezone=True),
        int: Integer,
        str: String,
    }
