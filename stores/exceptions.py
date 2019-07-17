from api.exceptions import ProjectBaseException
from stores import codes


class StoreNotAvailableException(ProjectBaseException):
    code = codes.stores_100_0


class StoreDoesNotBelongToWasherException(ProjectBaseException):
    code = codes.stores_100_1


class StoreHasSoManyImageException(ProjectBaseException):
    code = codes.stores_100_2


class StoreHasNoLogo(ProjectBaseException):
    code = codes.stores_100_3


class ImageDidNotDelete(ProjectBaseException):
    code = codes.stores_100_4
