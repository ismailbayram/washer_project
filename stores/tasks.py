from base.tasks import LockTask
from washer_project.celery import app


@app.task(base=LockTask)
def notify_stores_for_increasing():
    import datetime

    from django.utils import timezone
    from admin.stores.service import AdminStoreService
    from notifications.enums import NotificationType
    from notifications.service import NotificationService
    from stores.models import Store
    from reservations.enums import ReservationStatus

    store_service = AdminStoreService()
    for store in Store.objects.actives().iterator():
        max_reservation = store_service.get_weekly_reservation_count(store)

        now = timezone.now()
        this_monday = now - datetime.timedelta(days=now.weekday(),
                                               hours=now.hour, minutes=now.minute)
        next_monday = this_monday + datetime.timedelta(days=7)

        current_reservation_count = store.reservation_set.filter(
            start_datetime__lte=next_monday,
            start_datetime__gte=this_monday,
            status__gte=ReservationStatus.reserved,
        ).count()

        # todo: algoritma degismesi gerekebilir. haftanin kalan gunleri uzerinden bir hesap yapilabilir.
        # bu sekilde yaniltici olabilir.
        if max_reservation and current_reservation_count/max_reservation >= 0.8:
            notif_service = NotificationService()
            notif_service.send(instance=store, to=store,
                               notif_type=NotificationType.so_reservation_want_increase)


@app.task(name="stores.delete_store_index")
def delete_store_index(store_id):
    from search.indexer import StoreIndexer
    from stores.models import Store

    store = Store.objects.get(pk=store_id)
    store_indexer = StoreIndexer()
    store_indexer.delete_store(store)

# @app.task(name="stores.suspend_store")
# def suspend_store(store_id):
#     import pytz
#     from datetime import datetime
#     from django.conf import settings
#     from search.indexer import StoreIndexer
#     from stores.models import Store
#     from reservations.service import ReservationService
#
#     res_service = ReservationService()
#     store = Store.objects.get(pk=store_id)
#     timezone = pytz.timezone(settings.TIME_ZONE)
#     dt = timezone.localize(datetime.now())
#     # for reservation in store.reservation_set.filter(start_datetime__lt=dt):
#         # res_service.suspend(reservation)
#     store_indexer = StoreIndexer()
#     store_indexer.delete_store(store)
