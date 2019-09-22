from django.utils.translation import ugettext_lazy as _

from enumfields import Enum


class GroupTimeType(Enum):
    hour = "hour"
    month = "month"
    day = "day"

    class Labels:
        hour = _('hour')
        month = _('month')
        day = _('day')
