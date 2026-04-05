from pydantic import BaseModel

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.base import BaseRepository

from sqlalchemy import select, insert, delete

from src.repositories.mappers.mappers import FacilitiesDataMapper
from src.schemas.facilities import RoomFacilityAdd


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilitiesDataMapper


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm
    mapper = FacilitiesDataMapper

    async def set_room_facilities(self, room_id: int, facilities_ids: list[int]):
        query = select(self.model.facility_id).filter_by(room_id=room_id)
        res = await self.session.execute(query)
        current_facilities_ids: list[int] = res.scalars().all()

        ids_to_delete = list(set(current_facilities_ids) - set(facilities_ids))
        ids_to_insert = list(set(facilities_ids) - set(current_facilities_ids))

        if ids_to_delete:
            delete_m2m_facilities_stmt = delete(self.model).filter(
                self.model.room_id == room_id, self.model.facility_id.in_(ids_to_delete)
            )
            await self.session.execute(delete_m2m_facilities_stmt)

        if ids_to_insert:
            insert_m2m_facilities_stmt = insert(self.model).values(
                [{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_insert]
            )
            await self.session.execute(insert_m2m_facilities_stmt)

    async def edit_bulk(self, data: BaseModel, room_id: int) -> None:
        old_bulk_query = select(RoomsFacilitiesOrm).filter_by(room_id=room_id)
        result = await self.session.execute(old_bulk_query)
        models = result.scalars().all()

        exists_facilities_ids = []
        for model in models:
            exists_facilities_ids.append(
                (self.mapper.map_to_domain_entity(model)).model_dump()["facility_id"]
            )

        new_facilities_ids = data.model_dump()["facilities_ids"]

        delete_ids_list = list(set(exists_facilities_ids) - set(new_facilities_ids))

        not_same_ids = []
        for i in new_facilities_ids:
            if i in exists_facilities_ids:
                continue
            not_same_ids.append(i)

        _data = [
            RoomFacilityAdd(room_id=room_id, facility_id=facility_id)
            for facility_id in not_same_ids
        ]

        if delete_ids_list:
            for facility_id in delete_ids_list:
                await self.session.execute(
                    delete(RoomsFacilitiesOrm).filter_by(facility_id=facility_id)
                )

        if not_same_ids:
            await self.session.execute(
                insert(RoomsFacilitiesOrm).values([item.model_dump() for item in _data])
            )
