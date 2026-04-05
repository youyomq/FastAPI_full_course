from datetime import date

from fastapi import Query, Body, Path, APIRouter, HTTPException

from fastapi_cache.decorator import cache

from src.exceptions import ObjNotFoundException, IncorrectPairOfDatesException, check_pair_of_dates_is_correct, \
    HotelNotFoundHTTPException
from src.schemas.hotels import HotelAdd, HotelPatch
from src.api.dependencies import PaginationDep, DBDep

router = APIRouter(
    prefix="/hotels", tags=["Hotels"]
)  # with prefix we don't need add /hotel in each method


@router.get("")
#@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    date_from: date,
    date_to: date,
    title: str | None = Query(
        None, description="Hotel Title"
    ),  # query param http://127.0.0.1:8000/hotels?id=2&title=dubai & Optional(str) for older python versions
    location: str | None = Query(None, description="Hotel Location"),
):
    check_pair_of_dates_is_correct(date_from, date_to)

    return await db.hotels.get_filtered_by_time(
        location=location,
        title=title,
        limit=pagination.per_page,
        offset=pagination.per_page * (pagination.page - 1),
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{hotel_id}")
async def get_one_hotel(hotel_id: int, db: DBDep):
    try:
        return await db.hotels.get_one(id=hotel_id)
    except ObjNotFoundException:
        raise HotelNotFoundHTTPException

# request body
@router.post("/")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Sochi",
                "value": {
                    "title": "Sochi Hotel 5 stars next to marina.",
                    "location": "Sochi_Lux",
                },
            },
            "2": {
                "summary": "Dubai",
                "value": {
                    "title": "Dubai Hotel 5 stars next to ocean.",
                    "location": "Dubai_Lux",
                },
            },
        }
    ),
    # title: str #Don't recommend, we have to do it in DATA params, because it's not security
    # title: str = Body(embed=True) #embed need to format json when we have 1 param
    # name: str = Body()
):
    stmt = await db.hotels.add(hotel_data)
    await db.commit()

    return {"status": "ok", "data": stmt}

    # await session.commit() #commit делаем здесь так как внутри сессии можем работать с несколькими методами
    # print(add_hotel_stmt.compile(engine, compile_kwargs={'literal_binds': True})) # Debug!


@router.put("/{hotel_id}", summary="Full Data Update")
async def edit_hotel(db: DBDep, hotel_data: HotelAdd, hotel_id: int = Path()):
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()

    return {"status": "ok"}


@router.patch("/{hotel_id}", summary="Data Update")
async def update_data_hotel(db: DBDep, hotel_data: HotelPatch, hotel_id: int = Path()):
    await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()

    return {"status": "ok"}


@router.delete("/hotels/{hotel_id}")  # path param
async def delete_hotel(db: DBDep, hotel_id: int):
    await db.hotels.delete(id=hotel_id)
    await db.commit()

    return {"status": "ok"}
