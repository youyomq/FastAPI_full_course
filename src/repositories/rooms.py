from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.repositories.mappers.mappers import RoomDataMapper, RoomsDataWithRelsMapper
from src.repositories.utils import rooms_ids_for_booking


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_filtered_by_time(self, hotel_id: int, date_from: date, date_to: date):
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)

        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        result = await self.session.execute(query)
        return [
            RoomsDataWithRelsMapper.map_to_domain_entity(model)
            for model in result.scalars().all()
        ]

        # print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        # мое детище хорошо отработало, но не нужно(
        # async def get_all(self, hotel_id: int):
        #    query = (select(RoomsOrm)
        #             .filter(RoomsOrm.hotel_id==hotel_id))
        #    result = await self.session.execute(query)
        #    return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

        # async def get_one_or_none(self, hotel_rooms: list[BaseModel], room_id: int):
        #    for room in hotel_rooms:
        #        room = room.model_dump()
        #        if room["id"] == room_id:
        #            data = room
        #            return self.schema.model_validate(data, from_attributes=True)

    async def get_one_or_none_with_rels(self, **filter_by):
        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter_by(**filter_by)
        )

        result = await self.session.execute(query)

        model = result.scalars().one_or_none()

        if model is None:
            return None
        return RoomsDataWithRelsMapper.map_to_domain_entity(model)
