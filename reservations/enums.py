from django.utils.translation import ugettext_lazy as _

from enumfields import Enum


class ReservationStatus(Enum):
    available = '100'
    busy = '200'
    reserved = '300'
    started = '350'
    completed = '400'
    cancelled = '500'
    expired = '530'
    disabled = '560'

    class Labels:
        available = _('Available')
        busy = _('Busy')
        reserved = _('Reserved')
        started = _('Started')
        completed = _('Completed')
        cancelled = _('Cancelled')
        expired = _('Expired')
        disabled = _('Disabled')
