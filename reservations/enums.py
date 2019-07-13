from django.utils.translation import ugettext_lazy as _

from enumfields import Enum


class ReservationStatus(Enum):
    available = '100'
    occupied = '200'
    reserved = '300'
    started = '350'
    completed = '400'
    cancelled = '500'
    expired = '530'
    disabled = '560'

    class Labels:
        available = _('Available')
        occupied = _('Occupied')
        reserved = _('Reserved')
        started = _('Started')
        completed = _('Completed')
        cancelled = _('Cancelled')
        expired = _('Expired')
        disabled = _('Disabled')

    def __gt__(self, other):
        return int(self.value) > int(other.value)

    def __ge__(self, other):
        return int(self.value) >= int(other.value)

    def __lt__(self, other):
        return int(self.value) < int(other.value)

    def __le__(self, other):
        return int(self.value) <= int(other.value)
