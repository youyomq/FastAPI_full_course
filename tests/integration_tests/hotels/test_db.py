from src.schemas.hotels import HotelAdd


async def test_add_hotel(db):
    hotels_data = HotelAdd(title="Hotel 13 stars", location="St. Peterburg")

    new_hotel_stmt = await db.hotels.add(hotels_data)
    await db.commit()
    print(f"{new_hotel_stmt}")
