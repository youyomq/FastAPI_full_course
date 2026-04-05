from pydantic import BaseModel, Field, ConfigDict

from src.schemas.facilities import Facility


class RoomAddRequest(BaseModel):
    title: str
    description: str | None = Field(default=None)
    price: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0)
    facilities_ids: list[int] = []


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str | None = Field(default=None)
    price: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0)


class Room(RoomAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomWithRels(Room):
    facilities: list[Facility]


class RoomPatchRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int = Field(default=None, gt=0)
    quantity: int = Field(default=1, gt=0)
    facilities_ids: list[int] | None = None


class RoomPatch(BaseModel):
    hotel_id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int = Field(default=None, gt=0)
    quantity: int = Field(default=1, gt=0)
