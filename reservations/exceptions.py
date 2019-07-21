from api.exceptions import ProjectBaseException
from reservations import codes


class BasketEmptyException(ProjectBaseException):
    code = codes.reservations_100_0


class ReservationNotAvailableException(ProjectBaseException):
    code = codes.reservations_100_1


class ReservationOccupiedBySomeoneException(ProjectBaseException):
    code = codes.reservations_100_2


class ReservationStartedException(ProjectBaseException):
    code = codes.reservations_100_3


class ReservationCompletedException(ProjectBaseException):
    code = codes.reservations_100_4


class ReservationCanNotCancelledException(ProjectBaseException):
    code = codes.reservations_100_5


class ReservationExpiredException(ProjectBaseException):
    code = codes.reservations_100_6

class ReservationIsNotComplated(ProjectBaseException):
    code = codes.reservations_100_7

class ReservationHasNoComment(ProjectBaseException):
    code = codes.reservations_100_8
