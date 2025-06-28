from typing import TypeVar, Generic, Any, Generator

from sqlalchemy import (
    select,
    delete,
    update,
    insert,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self._model = model

    def _generate_where_clause(
        self, filter_dict: dict[str, Any]
    ) -> Generator[Any, None, None]:
        return (
            getattr(self._model, field) == value
            for field, value in filter_dict.items()
        )

    @property
    def _select_model(self):
        return select(self._model)

    async def get_multi(
        self,
        session: AsyncSession,
        filter_dict: dict[str, Any],
        offset: int = 0,
        limit: int = None,
    ) -> list[ModelType]:
        stmt = self._select_model.where(
            *self._generate_where_clause(filter_dict)
        ).offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_one(
        self, session: AsyncSession, filter_dict: dict[str, Any]
    ) -> ModelType:
        stmt = self._select_model.where(
            *self._generate_where_clause(filter_dict)
        )
        result = await session.execute(stmt)
        return result.scalars().one()

    async def create(
        self, session: AsyncSession, obj_in: dict[str, Any]
    ) -> ModelType:
        db_obj = self._model(**obj_in)
        session.add(db_obj)
        await session.flush([db_obj])
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        filter_dict: dict[str, Any],
        update_dict: dict[str, Any],
        is_patch=True,
        raise_on_not_affected=True,
    ) -> None:
        if is_patch:
            update_dict = {
                k: v for k, v in update_dict.items() if v is not None
            }
        stmt = (
            update(self._model)
            .where(*self._generate_where_clause(filter_dict))
            .values(**update_dict)
        )
        result = await session.execute(stmt)
        if raise_on_not_affected and not result.rowcount:
            raise Exception("NoResultFoundException")
        return None

    async def delete(
        self,
        session: AsyncSession,
        filter_dict: dict[str, Any],
        raise_on_not_affected=True,
    ) -> None:
        stmt = delete(self._model).where(
            *self._generate_where_clause(filter_dict)
        )
        result = await session.execute(stmt)
        await session.flush()
        if raise_on_not_affected and not result.rowcount:
            raise Exception("NoResultFoundException")
        return None

    async def bulk_insert(
        self,
        session: AsyncSession,
        obj_list: list[dict[str, Any]],
    ) -> None:
        stmt = insert(self._model).values(obj_list)
        await session.execute(stmt)
        return None
