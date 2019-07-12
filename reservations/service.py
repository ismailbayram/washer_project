import datetime
import pytz

from django.db.transaction import atomic
from django.utils.crypto import get_random_string
from django.conf import settings

from reservations.models import Reservation


timezone = pytz.timezone(settings.TIME_ZONE)


class ReservationService:
    # TODO: check basket is empty
    def _generate_reservation_number(self):
        number = get_random_string(length=10).upper()
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

    @atomic
    def create_week_from_config(self, store):
        config = store.config['reservation_hours']
        period = store.product_set.filter(is_primary=True).order_by('-period').first().period

        for k in range(1, 8):
            day_datetime = datetime.datetime.today() + datetime.timedelta(days=k)
            day = day_datetime.strftime("%A").lower()

            start = config[day]['start']
            end = config[day]['end']
            if start is None:
                continue

            start_time = datetime.datetime.strptime(start, "%H:%M")
            end_time = datetime.datetime.strptime(end, "%H:%M")
            diff = (end_time - start_time).seconds / 60
            period_count = int(diff / period)

            start_datetime = day_datetime.replace(hour=start_time.hour, minute=start_time.minute,
                                                  second=0)
            for p in range(period_count):
                start_dt = start_datetime + datetime.timedelta(minutes=(p * period))
                start_dt = timezone.localize(start_dt)
                self.create_reservation(store=store, start_datetime=start_dt, period=period)
