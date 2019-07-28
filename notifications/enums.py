from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class NotificationType(Enum):
    you_fired = 'you_fired'  # [to washer] you fired someone
    you_are_fired = 'you_are_fired'  # [to worker]
    you_are_moved_another_store = 'you_are_moved_another_store' # [to worker]
    you_moved_worker_to_store = 'you_moved_worker_to_store' # [to washer]
    you_has_new_worker = "you_has_new_worker" # [to washer]
    weekly_reservations_created = "weekly_reservations_created" # [to washer]
    reservation_disabled = "reservation_disabled" # [to store]
    reservation_expired = "reservation_expired" # [to store]
    reservation_reserved = "reservation_reserved" # [to store]

    reservation_started = "reservation_reserved" # [to store]
    reservation_completed = "reservation_completed" # [to store]
    reservation_canceled = "reservation_canceled" # [to store]

    store_approved = "store_approved" # [to washer]

    def get_view(self):
        view_map = {
            'you_fired': 'profile',
            'you_are_fired': 'profile',
            'you_are_moved_another_store': 'store',
            'you_moved_worker_to_store': 'store',
            'you_has_new_worker': 'profile',
            'weekly_reservations_created': 'store-reservations',
            'reservation_disabled': 'reservation',
            'reservation_expired': 'reservation',
            'reservation_reserved': 'reservation',
            'reservation_started': 'reservation',
            'reservation_completed': 'reservation',
            'reservation_canceled': 'reservation',
            'store_approved': 'store',
        }

        try:
            return view_map[self.value]
        except KeyError:
            raise NotImplementedError()


    def get_sentence(self, data):
        if self.value == 'you_are_moved_another_store':
            return _('Your store is changed to {store_name}.'.format(**data))

        if self.value == 'you_moved_worker_to_store':
            return _('You moved your {worker_name}orker to ({store_name}).'.format(**data))

        if self.value == 'you_fired':
            return _('You fired ({worker_name}).'.format(**data))

        if self.value == 'you_are_fired':
            return _('You are fired.')

        if self.value == 'you_has_new_worker':
            return _('You has a new worker. Wellcome {worker_name}.'.format(**data))

        if self.value == 'weekly_reservations_created':
            return _('Your weekly reservations has been created.')

        if self.value == 'reservation_disabled':
            return _('Reservation disabled')

        if self.value == 'reservation_expired':
            return _('Reservation expired')

        if self.value == 'reservation_reserved':
            return _('Reservation reserved.')

        if self.value == 'reservation_started':
            return _('Reservation started.')

        if self.value == 'reservation_completed':
            return _('Reservation complated.')

        if self.value == 'reservation_canceled':
            return _('Reservation canceled.')

        if self.value == 'store_approved':
            return _('Store Approved.')


        raise NotImplementedError()
