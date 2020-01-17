from api.exceptions import ProjectBaseException
from address import codes


class CityNotValidException(ProjectBaseException):
    code = codes.address_100_0


class TownshipNotValidException(ProjectBaseException):
    code = codes.address_100_1
