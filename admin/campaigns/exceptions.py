from api.exceptions import ProjectBaseException
from admin.campaigns import codes


class MultipleOneFreeInNineCampaignException(ProjectBaseException):
    code = codes.campaigns_100_0
