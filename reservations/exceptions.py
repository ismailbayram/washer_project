from api.exceptions import ProjectBaseException
from reservations import codes


class BasketEmptyException(ProjectBaseException):
    code = codes.reservations_100_0
