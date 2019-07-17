from api.exceptions import ProjectBaseException
from users import codes


class UserDoesNotExistException(ProjectBaseException):
    code = codes.users_100_0


class UserGroupTypeInvalidException(ProjectBaseException):
    code = codes.users_100_1


class WorkerDoesNotBelongToWasherException(ProjectBaseException):
    code = codes.workers_100_0

class SmsCodeIsNotCreated(ProjectBaseException):
    code = codes.workers_100_3

class SmsCodeExpired(ProjectBaseException):
    code = codes.workers_100_4

class SmsCodeIsInvalid(ProjectBaseException):
    code = codes.workers_100_5

class WorkerHasNoStore(ProjectBaseException):
    code = codes.workers_100_6
