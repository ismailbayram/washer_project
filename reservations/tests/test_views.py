import datetime
import json
from model_mommy import mommy
from decimal import Decimal
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.reverse import reverse_lazy
from rest_framework import status

from base.test import BaseTestViewMixin
from baskets.service import BasketService
from cars.enums import CarType
from cars.service import CarService
from products.service import ProductService
from reservations.service import ReservationService
from reservations.enums import ReservationStatus


@override_settings(DEFAULT_PRODUCT_PRICE=Decimal('20.00'))
class ReservationServiceTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.service = ReservationService()
        self.product_service = ProductService()
        self.car_service = CarService()
        self.basket_service = BasketService()
        self.init_users()
        self.customer_profile = self.customer.customer_profile
        self.customer2_profile = self.customer2.customer_profile
        self.store = mommy.make('stores.Store', washer_profile=self.washer.washer_profile,
                                is_approved=True, is_active=True)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2.washer_profile,
                                 is_approved=True, is_active=True)
        self.product1 = self.product_service.create_primary_product(self.store)
        self.product2 = self.product_service.create_product(name='Parfume', store=self.store,
                                                            washer_profile=self.store.washer_profile)
        self.product3 = self.product_service.create_primary_product(self.store2)
        self.car = self.car_service.create_car(licence_plate="34FH3773", car_type=CarType.normal,
                                               customer_profile=self.customer_profile)
        dt = timezone.now() + datetime.timedelta(minutes=30)
        self.reservation = self.service._create_reservation(self.store, dt, 40)
        self.reservation2 = self.service._create_reservation(self.store2, dt, 40)

    def test_list(self):
        url = reverse_lazy('api:router:reservations-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 0)

        self.service.occupy(self.reservation, self.customer_profile)
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve(self):
        url = reverse_lazy('api:router:reservations-detail', args=[self.reservation.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['pk'], self.reservation.pk)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_occupy(self):
        url = reverse_lazy('api:router:reservations-occupy', args=[self.reservation.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        import ipdb
        ipdb.set_trace()
        self.assertEqual(jresponse['pk'], self.reservation.pk)
        self.assertEqual(jresponse['status'], ReservationStatus.occupied.value)
