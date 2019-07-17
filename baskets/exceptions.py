from api.exceptions import ProjectBaseException
from baskets import codes


class PrimaryProductsQuantityMustOne(ProjectBaseException):
    code = codes.baskets_100_0


class BasketInvalidException(ProjectBaseException):
    code = codes.baskets_100_1
