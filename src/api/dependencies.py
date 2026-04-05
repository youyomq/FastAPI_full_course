from typing import Annotated

from fastapi import Depends, Query, Request, HTTPException
from pydantic import BaseModel

from src.database import async_session_maker
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    page: Annotated[
        int | None, Query(1, ge=1)
    ]  # считывает тип и то как он должен быть реализован
    per_page: Annotated[int | None, Query(5, ge=1, lt=30)]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request):
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="You ain't auth!")
    return token


def get_current_user_id(token: str = Depends(get_token)):
    data = AuthService().decode_token(token=token)
    return data.get("user_id", None)


UserIdDep = Annotated[int, Depends(get_current_user_id)]


def get_db_manager():
    return DBManager(session_factory=async_session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[
    DBManager, Depends(get_db)
]  # DBManager - просто аннотация для IDE, Depends(get_db) уже видит сам FastAPI
