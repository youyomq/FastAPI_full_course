import pytest


@pytest.fixture(scope="module")
async def clear_bookings(db_module):
    await db_module.bookings.delete()
    await db_module.commit()


@pytest.mark.parametrize(
    "room_id, date_from, date_to, booked_rooms",
    [
        (1, "2026-09-01", "2026-09-10", 1),
        (1, "2026-09-02", "2026-09-03", 2),
        (1, "2026-09-04", "2026-09-05", 3),
    ],
)
async def test_add_and_get_bookings(
    clear_bookings, room_id, date_from, date_to, booked_rooms, authenticated_ac, db
):

    response_bookings = await authenticated_ac.post(
        "/bookings",
        json={"room_id": room_id, "date_from": date_from, "date_to": date_to},
    )

    assert response_bookings.status_code == 200

    response_me = await authenticated_ac.get("/bookings/me")
    len_me_json = len(response_me.json()["data"])
    print(response_me.json())

    assert response_me.status_code == 200
    assert booked_rooms == len_me_json
