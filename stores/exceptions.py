from api.exceptions import ProjectBaseException
from stores import codes


class StoreDoesNotBelongToWasherException(ProjectBaseException):
    code = codes.stores_100_0
