from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class NotificationType(Enum):
    reservation_completed = 'reservation_completed'
    reservation_started = 'reservation_started'

    def get_sentence(self, data):
        if self.value == 'reservation_completed':
            return _('Your reservation has been completed')

        elif self.value == 'reservation_started':
            return _('Your reservation has been completed')
