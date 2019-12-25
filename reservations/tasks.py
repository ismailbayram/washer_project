from celery.schedules import crontab
from celery.task import periodic_task

from notifications.enums import NotificationType
from notifications.service import NotificationService
from washer_project.celery import app


@app.task(name="reservations.prevent_occupying_reservation")
def prevent_occupying_reservation(reservation_id):
    from reservations.models import Reservation
    from reservations.enums import ReservationStatus
    from search.indexer import ReservationIndexer
    reservation = Reservation.objects.get(pk=reservation_id)
    if reservation.status == ReservationStatus.occupied:
        reservation.customer_profile = None
        reservation.status = ReservationStatus.available
        reservation.save()
        res_indexer = ReservationIndexer()
        res_indexer.index_reservation(reservation)


@app.task(name="reservations.create_store_weekly_reservations")
def create_store_weekly_reservations(store_id):
    from stores.models import Store
    from reservations.models import Reservation
    from reservations.service import ReservationService
    from search.indexer import ReservationIndexer, StoreIndexer

    res_service = ReservationService()
    store = Store.objects.get(pk=store_id)
    res_pk_list = res_service.create_week_from_config(store)
    reservation_queryset = Reservation.objects.filter(pk__in=res_pk_list)
    store_indexer = StoreIndexer()
    store_indexer.index_store(store)
    res_indexer = ReservationIndexer()
    res_indexer.index_reservations(reservation_queryset)
    notif_service = NotificationService()
    notif_service.send(instance=store, to=store.washer_profile,
                       notif_type=NotificationType.weekly_reservations_created,)


@periodic_task(run_every=(crontab(minute='*/30')), name="reservations.check_expired_reservations")
def check_expired_reservations():
    import pytz
    from datetime import datetime
    from django.conf import settings
    from reservations.models import Reservation
    from reservations.enums import ReservationStatus
    from reservations.service import ReservationService
    from search.indexer import ReservationIndexer

    timezone = pytz.timezone(settings.TIME_ZONE)
    dt = timezone.localize(datetime.now())
    res_service = ReservationService()

    for reservation in Reservation.objects.filter(status=ReservationStatus.available,
                                                  start_datetime__lt=dt):
        res_service.expire(reservation)
    res_indexer = ReservationIndexer()
    res_indexer.delete_expired(dt)


@periodic_task(run_every=(crontab(hour='4', minute='0')), name="reservations.create_next_week_day")
def create_next_week_day():
    # every day at 4 am
    import datetime
    from stores.models import Store
    from reservations.models import Reservation
    from reservations.service import ReservationService
    from search.indexer import ReservationIndexer

    start_datetime = datetime.datetime.today() + datetime.timedelta(days=7)
    res_service = ReservationService()

    res_pk_list = []
    for store in Store.objects.actives():
        period = store.product_set.filter(is_primary=True).order_by('-period').first().period
        res_pk_list += res_service.create_day_from_config(store, start_datetime, period)

    reservation_queryset = Reservation.objects.filter(pk__in=res_pk_list)
    res_indexer = ReservationIndexer()
    res_indexer.index_reservations(reservation_queryset)
