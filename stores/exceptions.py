from api.exceptions import ProjectBaseException
from stores import codes


class StoreHasSoManyImageException(ProjectBaseException):
    code = codes.stores_100_0


class ImageDidNotDelete(ProjectBaseException):
    code = codes.stores_100_1


class StoreDoesNotBelongToWasherException(ProjectBaseException):
    code = codes.stores_100_2


class StoreHasNoLogo(ProjectBaseException):
    code = codes.stores_100_3
