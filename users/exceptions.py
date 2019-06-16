from api.exceptions import ProjectBaseException
from users import codes


class UserDoesNotExistException(ProjectBaseException):
    code = codes.users_100_0
