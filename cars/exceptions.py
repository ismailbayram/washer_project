from api.exceptions import ProjectBaseException
from cars import codes


class DublicateCarException(ProjectBaseException):
    code = codes.cars_100_0
