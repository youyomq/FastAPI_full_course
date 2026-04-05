from fastapi import APIRouter, HTTPException, Body

from src.api.dependencies import DBDep, UserIdDep
from src.exceptions import ObjNotFoundException, AllRoomsAreBookedException
from src.schemas.booking import BookingAddRequest, BookingAdd

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("")
async def get_all_bookings(db: DBDep):
    data = await db.bookings.get_all()
    return {"status": "ok", "data": data}


@router.get("/me")
async def get_me_bookings(db: DBDep, user_id: UserIdDep):
    try:
        user = await db.users.get_one(id=user_id)
    except ObjNotFoundException:
        raise HTTPException(status_code=400, detail="User doesn't Auth!")

    data = await db.bookings.get_filtered(user_id=user.id)
    return {"status": "ok", "data": data}


@router.post("")
async def add_booking(
    db: DBDep, user_id: UserIdDep, booking_data: BookingAddRequest = Body()
):
    try:
        await db.users.get_one(id=user_id)
    except ObjNotFoundException:
        raise HTTPException(status_code=400, detail="User doesn't Auth!")

    try:
        room = await db.rooms.get_one(id=booking_data.room_id)
    except ObjNotFoundException:
        raise HTTPException(status_code=400, detail="Room doesn't exist!")

    _booking_data = BookingAdd(
        user_id=user_id, price=room.price, **booking_data.model_dump()
    )

    try:
        booking = await db.bookings.add_new_booking(_booking_data)
    except AllRoomsAreBookedException:
        raise HTTPException(status_code=409, detail="All Rooms Are Booked")

    await db.commit()

    return {"status": "ok", "data": booking}
