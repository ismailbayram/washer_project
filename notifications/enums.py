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

    reservation_started = "reservation_started" # [to store]
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
            return None


    def get_sentence(self, data):
        tmp_data = {
            "store_name": None,
            "worker_name": None,
        }
        data = {**tmp_data, **data}

        sentenct_map = {
            # TODO: fix here
            'you_are_moved_another_store': _('You have been moved to {store_name}.'.format(**data)),
            'you_moved_worker_to_store':   _('You have moved your worker "{worker_name}" to {store_name}.'.format(**data)),
            'you_fired':                   _('You have fired a worker ({worker_name}).'.format(**data)),
            'you_are_fired':               _('You have fired.'),
            'you_has_new_worker':          _('You has a new worker. Wellcome {worker_name}.'.format(**data)),
            'weekly_reservations_created': _('Your weekly reservations has been created.'),
            'reservation_disabled':        _('Reservation disabled'),
            'reservation_expired':         _('Reservation expired'),
            'reservation_reserved':        _('Reservation reserved.'),
            'reservation_started':         _('Reservation started.'),
            'reservation_completed':       _('Reservation complated.'),
            'reservation_canceled':        _('Reservation canceled.'),
            'store_approved':              _('Store Approved.')
        }

        try:
            return sentenct_map[self.value]
        except KeyError:
            return None
