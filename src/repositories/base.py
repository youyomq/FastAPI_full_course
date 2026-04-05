import logging

from typing import Sequence

from asyncpg import UniqueViolationError
from sqlalchemy.exc import IntegrityError, NoResultFound

from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.testing.plugin.plugin_base import logging

from src.exceptions import ObjNotFoundException, ObjAlreadyExistsException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session  # Принимаем сессию извне, чтобы не создавать при каждом вызове метода

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)

        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        model = result.scalars().one_or_none()

        if model is None:
            return None

        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        try:
            model = result.scalars().one()
        except NoResultFound:
            raise ObjNotFoundException



        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        try:
            add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            result = await self.session.execute(add_stmt)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)

        except IntegrityError as ex:
            logging.exception(f"Can't add data to DB!")
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjAlreadyExistsException from ex
            else:
                logging.exception(f"Unknow Error!")
                raise ex


    async def add_bulk(self, data: Sequence[BaseModel]):
        add_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_stmt)

    async def edit(
        self, data: BaseModel, exclude_unset: bool = False, **filter_by
    ) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )  # атрибуты которые не были указаны не будут записаны в БД


        result = await self.session.execute(update_stmt)

        if result.rowcount == 0:
            raise ObjNotFoundException


    async def delete(self, **filter_by) -> None:
        delete_stmt = delete(self.model).filter_by(**filter_by)

        result = await self.session.execute(delete_stmt)

        if result.rowcount == 0:
            raise ObjNotFoundException
