from api.exceptions import ProjectBaseException
from notifications import codes


class BadUserProfileHeaderException(ProjectBaseException):
    code = codes.notifications_100_0
