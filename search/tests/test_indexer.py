import time
import datetime
from model_mommy import mommy

from django.test import TestCase, override_settings
from django.utils import timezone

from base.test import BaseTestViewMixin
from reservations.service import ReservationService
from products.service import ProductService
from search.documents import StoreDoc, ReservationDoc
from search.indexer import StoreIndexer, ReservationIndexer


@override_settings(ES_STORE_INDEX='test_stores', ES_RESERVATION_INDEX='test_reservations')
class StoreIndexerTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.init_users()
        self.indexer = StoreIndexer()
        self.res_service = ReservationService()
        self.product_service = ProductService()
        self.city = mommy.make('address.City')
        self.address = mommy.make('address.Address', city=self.city)
        self.address2 = mommy.make('address.Address', city=self.city)
        self.store = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                is_approved=True, is_active=True, address=self.address,
                                latitude=35, longitude=34)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=True, is_active=True, address=self.address2,
                                 latitude=35, longitude=34)
        self.product_service.create_primary_product(self.store)

    def test_index_store(self):
        self.indexer.index_store(self.store)
        time.sleep(1)
        query = StoreDoc.search().filter('match', pk=self.store.pk)
        response = query.execute()
        self.assertEqual(query.count().value, 1)
        self.assertEqual(response[0].pk, self.store.pk)

    def test_index_stores(self):
        self.indexer.index_stores(silence=True)
        time.sleep(1)
        query = StoreDoc.search().filter('match', city=self.city.pk)
        response = query.execute()
        self.assertEqual(query.count().value, 2)

    def test_delete_store(self):
        self.indexer.index_store(self.store)
        time.sleep(1)
        self.indexer.delete_store(self.store)
        time.sleep(1)
        query = StoreDoc.search().filter('match', pk=self.store.pk)
        response = query.execute()
        self.assertEqual(query.count().value, 0)

    def test_update_store_index(self):
        res_indexer = ReservationIndexer()
        self.indexer.index_store(self.store)
        dt = timezone.now() - datetime.timedelta(minutes=60)
        res1 = self.res_service._create_reservation(self.store, dt, 40)
        res_indexer.index_reservation(res1)
        time.sleep(1)

        self.store.name = "new name"
        self.store.save()
        self.indexer.update_store_index(self.store)
        time.sleep(1)

        query = StoreDoc.search().filter('match', pk=self.store.pk)
        response = query.execute()
        self.assertEqual(query.count().value, 1)
        self.assertEqual(response[0].name, "new name")

        query = ReservationDoc.search().filter({
            "match": {"store.pk": self.store.pk}
        })
        response = query.execute()
        self.assertEqual(response[0].store.name, "new name")


@override_settings(ES_STORE_INDEX='test_stores', ES_RESERVATION_INDEX='test_reservations')
class ReservationIndexerTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.init_users()
        self.indexer = ReservationIndexer()
        self.res_service = ReservationService()
        self.product_service = ProductService()
        self.city = mommy.make('address.City')
        self.address = mommy.make('address.Address', city=self.city)
        self.address2 = mommy.make('address.Address', city=self.city)
        self.store = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                is_approved=True, is_active=True, address=self.address,
                                latitude=35, longitude=34)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=True, is_active=True, address=self.address2,
                                 latitude=35, longitude=34)
        self.product_service.create_primary_product(self.store)
        self.product_service.create_primary_product(self.store2)
        dt = timezone.now()
        self.reservation = self.res_service._create_reservation(self.store, dt, 40)
        dt = dt + datetime.timedelta(minutes=40)
        self.reservation2 = self.res_service._create_reservation(self.store, dt, 40)

    def test_index_reservation(self):
        self.indexer.index_reservation(self.reservation)
        time.sleep(1)
        query = ReservationDoc.search().filter('match', pk=self.reservation.pk)
        response = query.execute()
        self.assertEqual(query.count().value, 1)
        self.assertEqual(response[0].pk, self.reservation.pk)

    def test_index_reservations(self):
        reservations = self.store.reservation_set.all()
        self.indexer.index_reservations(reservations, silence=True)
        time.sleep(1)
        query = ReservationDoc.search().filter({
            "match": {"store.pk": self.store.pk}
        })
        response = query.execute()
        self.assertEqual(query.count().value, 2)

    def test_delete_reservation(self):
        self.indexer.index_reservation(self.reservation)
        time.sleep(1)
        self.indexer.delete_reservation(self.reservation)
        time.sleep(1)
        query = ReservationDoc.search().filter('match', pk=self.reservation.pk)
        response = query.execute()
        self.assertEqual(query.count().value, 0)

    def test_delete_expired(self):
        dt = timezone.now() - datetime.timedelta(minutes=60)
        res1 = self.res_service._create_reservation(self.store, dt, 40)
        dt = timezone.now() - datetime.timedelta(minutes=120)
        res2 = self.res_service._create_reservation(self.store, dt, 40)
        self.indexer.index_reservation(res1)
        self.indexer.index_reservation(res2)
        time.sleep(1)

        self.indexer.delete_expired(timezone.now())
        time.sleep(1)

        query = ReservationDoc.search().filter('match', pk=res1.pk)
        response = query.execute()
        self.assertEqual(query.count().value, 0)

        query = ReservationDoc.search().filter('match', pk=res2.pk)
        response = query.execute()
        self.assertEqual(query.count().value, 0)


