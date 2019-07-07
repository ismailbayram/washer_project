from api.exceptions import ProjectBaseException
from products import codes


class PeriodIsRequiredException(ProjectBaseException):
    code = codes.product_100_0
