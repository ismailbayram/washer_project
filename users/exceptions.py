from api.exceptions import ProjectBaseException
from users import codes


class UserDoesNotExistException(ProjectBaseException):
    code = codes.users_100_0


class UserGroupTypeInvalidException(ProjectBaseException):
    code = codes.users_100_1


class StoreDoesNotBelongToWasherException(ProjectBaseException):
    code = codes.workers_100_0


class WorkerDoesNotBelongToWasherException(ProjectBaseException):
    code = codes.workers_100_1
