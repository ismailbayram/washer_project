from elasticsearch_dsl import UpdateByQuery
from django.utils import timezone
from django.conf import settings

from stores.models import Store
from products.models import Product
from reservations.models import Reservation
from reservations.enums import ReservationStatus
from search.documents import StoreDoc, ReservationDoc
from search.resources.serializers import StoreDocumentSerializer
from search.resources.serializers import ReservationDocumentSerializer


class StoreIndexer:
    def index_store(self, store):
        """
        :param store: Store
        :return: str
        """
        serializer = StoreDocumentSerializer(instance=store)
        doc = StoreDoc(**serializer.data)
        doc.meta.id = store.pk
        return doc.save(index=StoreDoc.Index.name)

    def index_stores(self, silence=False):
        """
        :return: None
        """
        q = Store.objects.actives().select_related('address',
                                                   'address__city',
                                                   'address__township')
        k = 0
        count = q.count()
        for store in q:
            k += 1
            resp = self.index_store(store)
            if not silence:
                print(f'{k}/{count} indexed of stores.[{resp}]')

    def update_store_index(self, store):
        """
        :param store: Store
        :return: None
        """
        self.index_store(store)
        serializer = StoreDocumentSerializer(instance=store)
        query = {
            "query": {
                "match": {"store.pk": store.pk}
            },
            "script": {
                "source": "ctx._source.store=params.store",
                "lang": "painless",
                "params": {
                    "store": serializer.data
                }
            }
        }
        ubq = UpdateByQuery(index=settings.ES_RESERVATION_INDEX).update_from_dict(query)
        ubq.execute()

    def delete_store(self, store):
        """
        :param store: Store
        :return: None
        """
        doc = StoreDoc().get(id=store.pk)
        doc.delete(id=store.pk)
        ReservationDoc.search().filter({"match": {"store.pk": store.pk}}).delete()


class ReservationIndexer:
    def index_reservation(self, reservation):
        """
        :param reservation: Reservation
        :return: None
        """
        serializer = ReservationDocumentSerializer(instance=reservation)
        store_data = serializer.data.get('store')
        doc = ReservationDoc(**serializer.data)
        doc.meta.id = reservation.pk
        doc.store = store_data

        price = {}
        product = Product.objects.filter(store=reservation.store, is_primary=True)\
                                 .prefetch_related('productprice_set').first()
        for pp in product.productprice_set.all():
            price[pp.car_type.value] = float(pp.price)
        doc.price = price

        return doc.save(index=ReservationDoc.Index.name)

    def index_reservations(self, res_list=None, silence=False):
        """
        :return: None
        """
        now = timezone.now()
        q = res_list or Reservation.objects.filter(status__in=[ReservationStatus.available,
                                                               ReservationStatus.occupied],
                                                   store__is_approved=True, store__is_active=True,
                                                   start_datetime__gt=now)\
            .select_related('store', 'store__address', 'store__address__city', 'store__address__township')
        k = 0
        count = q.count()
        for reservation in q:
            k += 1
            resp = self.index_reservation(reservation)
            if not silence:
                print(f'{k}/{count} indexed of reservations.[{resp}]')

    def delete_reservation(self, reservation):
        """
        :param reservation: Reservation
        :return: None
        """
        doc = ReservationDoc().get(id=reservation.pk, ignore=404)
        if doc:
            doc.delete(id=reservation.pk)

    def delete_expired(self, datetime):
        """
        :param datetime: Datetime
        :return: None
        """
        ReservationDoc.search().filter({"match": {"status": ReservationStatus.available.value}})\
                               .filter({"range": {"start_datetime": {"lte": datetime.isoformat()}}})\
                               .delete()
