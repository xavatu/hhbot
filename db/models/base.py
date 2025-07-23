import datetime
import uuid

from croniter import croniter
from sqlalchemy import DateTime, Integer, UUID
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


class UUIDString(TypeDecorator):
    impl = UUID
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except Exception:
            raise ValueError(f"Invalid UUID: {value}")

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return str(value)


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime.datetime: DateTime(timezone=True),
        int: Integer,
        str: String,
    }
