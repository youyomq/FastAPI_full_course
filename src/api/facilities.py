from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.schemas.facilities import FacilityAdd
from src.api.dependencies import DBDep
# from src.tasks.tasks import test_task

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.get("")
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post("/add")
async def create_facility(db: DBDep, facility_data: FacilityAdd):
    facility = await db.facilities.add(facility_data)
    await db.commit()

    # test_task.delay() #sync, but not block

    return {"status": "ok", "data": facility}
