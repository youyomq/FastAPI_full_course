import pytest


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (1, "2026-01-01", "2026-01-10", 200),
        (1, "2026-01-02", "2026-01-11", 200),
        (1, "2026-01-03", "2026-01-12", 200),
        (1, "2026-01-04", "2026-01-13", 200),
        (1, "2026-01-05", "2026-01-14", 200),
        (1, "2026-01-06", "2026-01-15", 409),
    ],
)
async def test_add_booking(
    room_id, date_from, date_to, status_code, authenticated_ac, db
):
    response = await authenticated_ac.post(
        "/bookings",
        json={"room_id": room_id, "date_from": date_from, "date_to": date_to},
    )

    assert response.status_code == status_code

    if status_code == 200:
        res = response.json()

        assert isinstance(res, dict)
        assert res["status"] == "ok"
        assert "data" in res
