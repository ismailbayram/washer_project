from django.utils import timezone

from stores.models import Store
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

    def index_stores(self):
        """
        :return: None
        """
        q = Store.objects.filter(is_approved=True, is_active=True) \
            .select_related('address', 'address__city', 'address__township')
        k = 0
        count = q.count()
        for store in q:
            k += 1
            resp = self.index_store(store)
            print(f'{k}/{count} indexed of stores.[{resp}]')

    def delete_store(self, store):
        """
        :param store: Store
        :return: None
        """
        doc = StoreDoc()
        doc.delete(id=store.pk)


class ReservationIndexer:
    def index_reservation(self, reservation):
        """
        :param reservation: Reservation
        :return: None
        """
        serializer = ReservationDocumentSerializer(instance=reservation)
        doc = ReservationDoc(**serializer.data)
        doc.meta.id = reservation.pk
        return doc.save(index=ReservationDoc.Index.name)

    def index_reservations(self):
        """
        :return: None
        """
        now = timezone.now()
        q = Reservation.objects.filter(status__in=[ReservationStatus.available, ReservationStatus.occupied],
                                       store__is_approved=True, store__is_active=True, start_datetime__gt=now)\
            .select_related('store', 'store__address', 'store__address__city', 'store__address__township')
        k = 0
        count = q.count()
        for store in q:
            k += 1
            resp = self.index_reservation(store)
            print(f'{k}/{count} indexed of reservations.[{resp}]')

    def delete_reservation(self, reservation):
        """
        :param reservation: Reservation
        :return: None
        """
        doc = ReservationDoc()
        doc.delete(id=reservation.pk)
