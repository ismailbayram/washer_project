import logging

from django.utils.translation import ugettext_lazy as _
from enumfields import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    you_fired = 'you_fired'  # [to washer] you fired someone
    you_are_fired = 'you_are_fired'  # [to worker]
    you_are_moved_another_store = 'you_are_moved_another_store'  # [to worker]

    you_moved_worker_to_store = 'you_moved_worker_to_store'  # [to washer]
    you_has_new_worker = 'you_has_new_worker'  # [to washer]
    weekly_reservations_created = 'weekly_reservations_created'  # [to washer]

    reservation_disabled = 'reservation_disabled'  # [to store]
    reservation_expired = 'reservation_expired'  # [to store]
    reservation_reserved = 'reservation_reserved'  # [to store]
    reservation_reminder_c = 'reservation_reminder_c'  # [to customer]
    reservation_reminder_s = 'reservation_reminder_s'  # [to store]
    reservation_started = 'reservation_started'  # [to store]
    reservation_completed = 'reservation_completed'  # [to store]
    reservation_cancelled = 'reservation_cancelled'  # [to store]
    so_reservation_want_increase = 'so_reservation_want_increase'  # [to store]

    store_approved = "store_approved"  # [to washer]

    def get_view(self):
        """with views (and view_id which set on services set() method, mobile
        app will know the redirection of page"""
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
            'reservation_reminder_c': 'reservation',
            'reservation_reminder_s': 'reservation',
            'reservation_started': 'reservation',
            'reservation_completed': 'reservation',
            'reservation_cancelled': 'reservation',
            'so_reservation_want_increase': 'store',
            'store_approved': 'store',
        }

        try:
            return view_map[self.value]
        except KeyError as e:
            logger.exception(e)
            return None

    def get_sentence(self, data):
        tmp_data = {
            "store_name": None,
            "worker_name": None,
        }
        data = {**tmp_data, **data}

        sentence_map = {
            'you_are_moved_another_store': _('You have been moved to another store: {store_name}.'.format(**data)),
            'you_moved_worker_to_store':   _('You moved {worker_name} to ({store_name}).'.format(**data)),
            'you_fired':                   _('You fired ({worker_name}).'.format(**data)),
            'you_are_fired':               _('You are fired.'),
            'you_has_new_worker':          _('You have a new worker. Welcome to {worker_name}.'.format(**data)),
            'weekly_reservations_created': _('Your weekly reservations has been created.'),
            'reservation_disabled':        _('Reservation disabled by system.'),
            'reservation_expired':         _('Reservation expired'),
            'reservation_reserved':        _('Reservation reserved.'),
            'reservation_reminder_c':      _('You have a reservation after 30 minutes.'),
            'reservation_reminder_s':      _('A customer is going to come after 30 minutes.'),
            'reservation_started':         _('Reservation process started.'),
            'reservation_completed':       _('Reservation process completed.'),
            'reservation_cancelled':       _('Reservation cancelled by washer.'),
            'so_reservation_want_increase': _('Your store filled 80% of appointments in this week. Don\'t you think increase reservation hours?'),
            'store_approved':              _('Your store has been approved.')

        }

        try:
            return sentence_map[self.value]
        except KeyError as e:
            logger.exception(e)
            return None
