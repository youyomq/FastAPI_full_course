from fastapi import APIRouter, HTTPException, Response, Request

from src.exceptions import ObjAlreadyExistsException
from src.schemas.users import UserRequestAdd, UserAdd
from src.api.dependencies import UserIdDep, DBDep

from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authorization & Authentication"])


@router.post("/register")
async def register_user(db: DBDep, data: UserRequestAdd):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)

    try:
        await db.users.add(new_user_data)
        await db.commit()
    except ObjAlreadyExistsException:
        raise HTTPException(status_code=400, detail="User Already Exists!")

    return {"status": "ok"}


@router.post("/login")
async def login_user(db: DBDep, data: UserRequestAdd, response: Response):
    user = await db.users.get_user_with_hashed_password(email=data.email)

    if not user:
        raise HTTPException(status_code=401, detail="User doesn't exist!")
    access_token = AuthService().create_access_token({"user_id": user.id})

    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect Password!")

    response.set_cookie(
        "access_token", access_token
    )  # при каждом запросе будет автоматически отправляться coock'а
    return {"status": "ok", "access_token": f"{access_token}"}


@router.get("/me")
async def get_me(db: DBDep, user_id: UserIdDep, request: Request):
    user = await db.users.get_one_or_none(id=user_id)
    access_token = request.cookies.get("access_token")

    return {"status": "ok", "user_data": user, "access_token": f"{access_token}"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")

    return {"status": "ok"}
