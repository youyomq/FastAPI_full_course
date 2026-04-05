from datetime import date

from fastapi import HTTPException
from sqlalchemy import select, insert, func
from sqlalchemy.sql.functions import coalesce

from src.models import RoomsOrm
from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper
from src.schemas.booking import BookingAddRequest


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self):
        query = select(BookingsOrm).filter(BookingsOrm.date_from == date.today())

        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res]

    async def add_new_booking(self, data: BookingAddRequest):
        room_quantity_query = (
            select(RoomsOrm.id, RoomsOrm.quantity.label("room_count"))
            .filter(RoomsOrm.id == data.room_id)
            .group_by(RoomsOrm.id)
            .cte("room_count")
        )

        room_bookings_query = (
            select(BookingsOrm.room_id, func.count("*").label("booking_count"))
            .select_from(BookingsOrm)
            .filter(
                BookingsOrm.room_id == data.room_id,
                BookingsOrm.date_from < data.date_to,
                BookingsOrm.date_to > data.date_from,
            )
            .group_by(BookingsOrm.room_id)
            .cte("room_bookings")
        )

        res_count_query = (
            select(
                room_quantity_query.c.room_count
                - coalesce(room_bookings_query.c.booking_count, 0)
            )
            .select_from(room_quantity_query)
            .outerjoin(
                room_bookings_query,
                room_quantity_query.c.id == room_bookings_query.c.room_id,
            )
        )

        res_count = (await self.session.execute(res_count_query)).scalar()

        print(res_count)

        if res_count >= 1:
            add_stmt = insert(BookingsOrm).values(**data.model_dump())
            await self.session.execute(add_stmt)
        else:
            raise HTTPException(status_code=409, detail="Room Busy!")
