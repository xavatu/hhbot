import datetime

from croniter import croniter
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator, String


class CronSchedule(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not croniter.is_valid(value):
            raise ValueError(f"Invalid cron expression: {value}")
        return value

    def process_result_value(self, value, dialect):
        return value


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime.datetime: DateTime(timezone=True),
        int: Integer,
        str: String,
    }
