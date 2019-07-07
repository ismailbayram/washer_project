from api.exceptions import ProjectBaseException
from stores import codes


class StoreHasSoMuchImageException(ProjectBaseException):
    code = codes.stores_100_0
