from api.exceptions import ProjectBaseException

from admin.stores import codes


class StoreIsAlreadyApproved(ProjectBaseException):
    code = codes.admin_stores_100_0


class StoreIsAlreadyDeclined(ProjectBaseException):
    code = codes.admin_stores_100_1
