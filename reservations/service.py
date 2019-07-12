import random
import datetime

from reservations.models import Reservation
from reservations.enums import ReservationStatus


class ReservationService:
    # TODO: check basket is empty
    def _generate_reservation_number(self):
        # TODO: make this str
        number = str(random.randint(10_000_000_000, 99_999_999_999))
        if Reservation.objects.filter(number=number).exists():
            return self._generate_reservation_number()
        return number

    def create_reservation(self, store, start_datetime, period):
        """
        :param store: Store
        :param start_datetime: DateTime
        :param period: int
        :return: Reservation
        """
        try:
            reservation = Reservation.objects.get(store=store, start_datetime=start_datetime)
        except Reservation.DoesNotExist:
            end_datetime = start_datetime + datetime.timedelta(minutes=period)
            reservation = Reservation.objects.create(store=store, start_datetime=start_datetime,
                                                     end_datetime=end_datetime, period=period,
                                                     number=self._generate_reservation_number())

        return reservation
