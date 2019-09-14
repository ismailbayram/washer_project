from api.exceptions import ProjectBaseException
from users import codes


class UserDoesNotExistException(ProjectBaseException):
    code = codes.users_100_0


class UserGroupTypeInvalidException(ProjectBaseException):
    code = codes.users_100_1


class WorkerDoesNotBelongToWasherException(ProjectBaseException):
    code = codes.workers_100_0

class SmsCodeIsNotCreatedException(ProjectBaseException):
    code = codes.auth_100_0

class SmsCodeExpiredException(ProjectBaseException):
    code = codes.auth_100_1

class SmsCodeIsInvalidException(ProjectBaseException):
    code = codes.auth_100_2

class WorkerHasNoStoreException(ProjectBaseException):
    code = codes.auth_100_3

class ThereIsUserGivenPhone(ProjectBaseException):
    code = codes.auth_100_4
