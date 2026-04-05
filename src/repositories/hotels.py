from datetime import date
from pydantic import BaseModel

from src.exceptions import IncorrectPairOfDatesException
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.models.hotels import HotelsOrm
from sqlalchemy import select, func

from src.repositories.mappers.mappers import HotelDataMapper
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsOrm  # зависим от объектов sqlalchemy -> нужен Data Mapper
    mapper = HotelDataMapper  # репозиторий отвязан и не знает как преобразуются данные
    schema = Hotel

    async def get_all(self, location, title, limit, offset) -> list[BaseModel]:
        query = select(HotelsOrm)

        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.lower()))
        if location:
            query = query.where(
                func.lower(HotelsOrm.location).contains(location.lower())
            )

        query = query.limit(limit).offset(
            offset
        )  # query for select, statement for insert, etc.

        result = await self.session.execute(query)

        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

        # print(result, type(result)) # Data hide in Iterator Object

        # hotels_ = result.all()
        # print(hotels_, type(hotels_)) #tuple - (HotelsORM(id=1, title='a', location='b'), )

        # if pagination.page and pagination.per_page:
        #   return hotels_[pagination.per_page*(pagination.page-1):pagination.per_page*pagination.page]
        # print(query_.compile(compile_kwargs={'literal_binds': True}))

    async def get_filtered_by_time(
        self, location, title, limit, offset, date_from: date, date_to: date
    ):
        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)

        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        query = select(HotelsOrm.id).filter(HotelsOrm.id.in_(hotels_ids_to_get))

        if location:
            query = query.filter(
                func.lower(HotelsOrm.location).contains(location.lower())
            )
        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.lower()))

        query = query.limit(limit).offset(offset)

        return await self.get_filtered(HotelsOrm.id.in_(query))
