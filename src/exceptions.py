from datetime import date
from fastapi import HTTPException


class NabronirovaliException(Exception):
    detail = "Error!"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

class ObjNotFoundException(NabronirovaliException):
    detail = "Object Didn't Found"


class ObjAlreadyExistsException(NabronirovaliException):
    detail = "Object Already Exists!"


class AllRoomsAreBookedException(NabronirovaliException):
    detail = "All Rooms Are Booked"


class ObjNotExistsException(NabronirovaliException):
    detail = "Object Doesn't Exist"


class IncorrectPairOfDatesException(NabronirovaliException):
    detail = "Date From bigger Than Date To!"

def check_pair_of_dates_is_correct(date_from: date, date_to: date) -> None:
    if date_from >= date_to:
        raise HTTPException(status_code=422, detail=IncorrectPairOfDatesException.detail)

class NabronirovaliHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self, *args, **kwargs):
        super().__init__(status_code=self.status_code, detail=self.detail)

class HotelNotFoundHTTPException(NabronirovaliHTTPException):
    status_code = 404
    detail = "Hotel Not Found"

class RoomNotFoundHTTPException(NabronirovaliHTTPException):
    status_code = 404
    detail = "Room Not Found"