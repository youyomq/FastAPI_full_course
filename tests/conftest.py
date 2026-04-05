# ruff: noqa: E402
# ruff: noqa: F403

import json
from typing import AsyncGenerator
from unittest import mock


mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

import pytest

from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.database import Base, engine_null_pull, async_session_maker_null_pool
from src.main import app
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.api.dependencies import get_db
from src.models import *
from src.utils.db_manager import DBManager


@pytest.fixture(scope="session", autouse=True)
async def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool() -> DBManager:
    async with DBManager(session_factory=async_session_maker_null_pool) as db_null_pull:
        yield db_null_pull


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="function")  # can't use in session fixture
async def db() -> AsyncGenerator[DBManager]:
    async for db in get_db_null_pool():
        yield db


@pytest.fixture(scope="module")  # can't use in session fixture
async def db_module() -> AsyncGenerator[DBManager]:
    async for db in get_db_null_pool():
        yield db


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pull.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def add_test_data(setup_database):
    with open(r"tests\mock_hotels.json", encoding="utf-8") as file_hotels:
        hotels_json = json.load(file_hotels)

    with open(r"tests\mock_rooms.json", encoding="utf-8") as file_rooms:
        rooms_json = json.load(file_rooms)

    hotels_bulk = [HotelAdd.model_validate(hotel) for hotel in hotels_json]
    rooms_bulk = [RoomAdd.model_validate(room) for room in rooms_json]

    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(hotels_bulk)
        await db_.rooms.add_bulk(rooms_bulk)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(ac, setup_database):
    await ac.post(
        "/auth/register", json={"email": "test1@gmail.com", "password": "12345"}
    )


@pytest.fixture(scope="session")
async def authenticated_ac(register_user, ac):
    response_login = await ac.post(
        "/auth/login", json={"email": "test1@gmail.com", "password": "12345"}
    )

    assert response_login.status_code == 200

    response_get_me = await ac.get("/auth/me")

    access_token = response_get_me.json()
    assert response_get_me.status_code == 200
    print(access_token)
    assert access_token["access_token"] == ac.cookies["access_token"]

    yield ac
