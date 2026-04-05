import pytest


@pytest.mark.parametrize(
    "email, password, status_code",
    [("user@example.com", "1234", 200), ("user7@example.com", "1234", 200)],
)
async def test_auth_flow(
    email,
    password,
    status_code,
    ac,
):
    # reg
    response_reg = await ac.post(
        "/auth/register", json={"email": email, "password": password}
    )

    assert response_reg.status_code == status_code

    # login
    response_log = await ac.post(
        "/auth/login", json={"email": email, "password": password}
    )

    assert response_log.status_code == status_code
    assert ac.cookies["access_token"]

    # me
    response_me = await ac.get("/auth/me")

    user = response_me.json()
    print(user)
    assert response_me.status_code == status_code
    assert "access_token" in user
    assert ac.cookies["access_token"]

    assert "password" not in user["user_data"]
    assert "hashed_password" not in user["user_data"]
    assert "email" in user["user_data"]

    # logout
    response_logout = await ac.post("/auth/logout")

    response_me_after_logout = await ac.get("/auth/me")

    assert response_logout.status_code == status_code
    assert response_me_after_logout.status_code == 401

    assert "data" not in response_me_after_logout.json()
