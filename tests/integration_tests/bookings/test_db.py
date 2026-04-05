from datetime import date

from src.schemas.booking import BookingAdd


async def test_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id

    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2026, month=3, day=2),
        date_to=date(year=2026, month=3, day=7),
        price=130,
    )

    new_booking = await db.bookings.add(booking_data)

    # get booking
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert booking
    assert booking.id == new_booking.id
    assert booking.room_id == new_booking.room_id

    # update
    updated_booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2026, month=5, day=3),
        date_to=date(year=2026, month=5, day=5),
        price=130,
    )

    await db.bookings.edit(updated_booking_data)
    updated_booking = await db.bookings.get_one_or_none(id=booking.id)

    assert updated_booking.date_from == updated_booking_data.date_from
    assert updated_booking.date_to == updated_booking_data.date_to
    assert updated_booking.price == updated_booking_data.price

    # delete
    await db.bookings.delete(id=booking.id)
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert not booking
