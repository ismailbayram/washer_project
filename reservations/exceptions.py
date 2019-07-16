from api.exceptions import ProjectBaseException
from reservations import codes


class BasketEmptyException(ProjectBaseException):
    code = codes.reservations_100_0


class ReservationNotAvailableException(ProjectBaseException):
    code = codes.reservations_100_1


class ReservationOccupiedBySomeoneException(ProjectBaseException):
    code = codes.reservations_100_2
