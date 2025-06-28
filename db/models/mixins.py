import re

from sqlalchemy.orm import declared_attr

REGULAR_COMP = re.compile(r"((?<=[a-z\d])[A-Z]|(?!^)[A-Z](?=[a-z]))")


def camel_to_snake(camel_string):
    return REGULAR_COMP.sub(r"_\1", camel_string).lower()


class TableNameMixin:
    @classmethod
    def __generate_table_snake_name(cls):
        return camel_to_snake(cls.__name__)

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__generate_table_snake_name()
