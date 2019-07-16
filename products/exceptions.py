from api.exceptions import ProjectBaseException
from products import codes


class PeriodIsRequiredException(ProjectBaseException):
    code = codes.product_100_0


class PrimaryProductsCanNotDeletedException(ProjectBaseException):
    code = codes.product_100_1


class ProductPriceCanNotLessThanException(ProjectBaseException):
    code = codes.product_100_2
