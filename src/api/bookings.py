from fastapi import APIRouter, HTTPException, Body

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.booking import BookingAddRequest, BookingAdd

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("")
async def get_all_bookings(db: DBDep):
    data = await db.bookings.get_all()
    return {"status": "ok", "data": data}


@router.get("/me")
async def get_me_bookings(db: DBDep, user_id: UserIdDep):
    user = await db.users.get_one_or_none(id=user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User ain't auth")

    data = await db.bookings.get_filtered(user_id=user.id)
    return {"status": "ok", "data": data}


@router.post("")
async def add_booking(
    db: DBDep, user_id: UserIdDep, booking_data: BookingAddRequest = Body()
):
    user = await db.users.get_one_or_none(id=user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User ain't auth")

    room = await db.rooms.get_one_or_none(id=booking_data.room_id)

    if not room:
        raise HTTPException(status_code=401, detail="Room doesn't exist!")

    _booking_data = BookingAdd(
        user_id=user_id, price=room.price, **booking_data.model_dump()
    )

    booking = await db.bookings.add_new_booking(_booking_data)
    await db.commit()

    return {"status": "ok", "data": booking}
