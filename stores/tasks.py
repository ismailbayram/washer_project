from washer_project.celery import app


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
