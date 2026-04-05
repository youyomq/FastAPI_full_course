from datetime import date

from fastapi import APIRouter, Body, Query
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPatch
from src.schemas.facilities import RoomFacilityAdd

router = APIRouter(prefix="/hotels", tags=["Rooms"])


@router.get("/{hotel_id}/rooms")
# @cache(expire=10)
async def get_rooms(
    db: DBDep,
    hotel_id: int,
    date_from: date = Query(examples=["2026-08-01"]),
    date_to: date = Query(examples=["2026-08-10"]),
):
    hotel_rooms = await db.rooms.get_filtered_by_time(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )

    return {"status": "ok", "data": hotel_rooms}


@router.get("/{hotel_id}/rooms/{room_id}")
@cache(expire=10)
async def get_one_room(db: DBDep, hotel_id: int, room_id: int):
    result = await db.rooms.get_one_or_none_with_rels(id=room_id, hotel_id=hotel_id)

    return {"status": "ok", "data": result}


@router.post("/{hotel_id}/rooms/add_room")
async def create_room(db: DBDep, hotel_id=int, room_data: RoomAddRequest = Body()):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)

    rooms_facilities_data = [
        RoomFacilityAdd(room_id=room.id, facility_id=f_id)
        for f_id in room_data.facilities_ids
    ]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()

    return {"status": "ok", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def edit_room(db: DBDep, hotel_id: int, room_id: int, room_data: RoomAddRequest):
    _room_data = RoomPatch(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(data=_room_data, id=room_id, hotel_id=hotel_id)
    await db.rooms_facilities.edit_bulk(room_data, room_id=room_id)
    await db.commit()

    return {"status": "ok"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def update_room(
    db: DBDep, hotel_id: int, room_id: int, room_data: RoomPatchRequest
):
    _room_data_dict = room_data.model_dump(exclude_unset=True)
    _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)
    await db.rooms.edit(data=_room_data, exclude_unset=True, id=room_id)

    if "facilities_ids" in _room_data_dict:
        await db.rooms_facilities.edit_bulk(room_data, room_id=room_id)

    await db.commit()

    return {"status": "ok"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(db: DBDep, hotel_id: int, room_id: int):
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()

    return {"status": "ok"}
