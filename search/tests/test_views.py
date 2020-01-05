import time
import json
import datetime
from rest_framework.reverse import reverse_lazy
from model_mommy import mommy

from django.test import TestCase, override_settings
from django.utils import timezone

from base.test import BaseTestViewMixin
from reservations.service import ReservationService
from products.service import ProductService
from search.indexer import StoreIndexer, ReservationIndexer


class StoreSearchViewTest(TestCase, BaseTestViewMixin):
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
                                 latitude=35, longitude=40)
        self.product_service.create_primary_product(self.store)
        self.indexer.index_stores(silence=True)
        time.sleep(1)

    def test_view(self):
        url = reverse_lazy('api:store_search')

        query_params = f'?city={self.city.pk}'
        response = self.client.get(f'{url}{query_params}')
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)


class ReservationSearchViewTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.init_users()
        self.indexer = ReservationIndexer()
        self.store_indexer = StoreIndexer()
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
        dt = timezone.now() + datetime.timedelta(minutes=30)
        self.reservation = self.res_service._create_reservation(self.store, dt, 40)
        dt = dt + datetime.timedelta(minutes=40)
        self.reservation2 = self.res_service._create_reservation(self.store, dt, 40)
        self.indexer.index_reservations(silence=True)
        self.store_indexer.index_stores(silence=True)
        time.sleep(1)

    def test_view(self):
        url = reverse_lazy('api:reservation_search')

        query_params = f'?city={self.city.pk}'
        response = self.client.get(f'{url}{query_params}')
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)
