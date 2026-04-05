from pydantic import BaseModel, Field, ConfigDict


class HotelAdd(BaseModel):
    title: str
    location: str


class Hotel(HotelAdd):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )  # позволяет pydantic читать данные из объектов, а не только из словарей


class HotelPatch(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)
