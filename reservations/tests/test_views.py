import datetime
import json
from model_mommy import mommy
from django.test import TestCase
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


class CustomerReservationViewSetTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.service = ReservationService()
        self.product_service = ProductService()
        self.car_service = CarService()
        self.basket_service = BasketService()
        self.init_users()
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
        self.assertEqual(jresponse['pk'], self.reservation.pk)
        self.assertEqual(jresponse['status'], ReservationStatus.occupied.value)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer2_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reserve(self):
        url_occupy = reverse_lazy('api:router:reservations-occupy', args=[self.reservation.pk])
        url = reverse_lazy('api:router:reservations-reserve', args=[self.reservation.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url_occupy, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        basket = self.basket_service.get_or_create_basket(self.customer_profile)
        self.basket_service.add_basket_item(basket, self.product1)
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['pk'], self.reservation.pk)
        self.assertEqual(jresponse['status'], ReservationStatus.reserved.value)


class StoreReservationViewSetTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.service = ReservationService()
        self.product_service = ProductService()
        self.car_service = CarService()
        self.basket_service = BasketService()
        self.init_users()
        self.store = mommy.make('stores.Store', washer_profile=self.washer.washer_profile,
                                is_approved=True, is_active=True)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2.washer_profile,
                                 is_approved=True, is_active=True)
        self.store3 = mommy.make('stores.Store', washer_profile=self.washer2.washer_profile,
                                 is_approved=True, is_active=True)
        self.product1 = self.product_service.create_primary_product(self.store)
        self.product2 = self.product_service.create_product(name='Parfume', store=self.store,
                                                            washer_profile=self.store.washer_profile)
        self.product3 = self.product_service.create_primary_product(self.store2)
        self.car = self.car_service.create_car(licence_plate="34FH3773", car_type=CarType.normal,
                                               customer_profile=self.customer_profile)
        dt = timezone.now() + datetime.timedelta(minutes=30)
        dt2 = dt + datetime.timedelta(minutes=30)
        self.reservation = self.service._create_reservation(self.store, dt, 30)
        self.reservation2 = self.service._create_reservation(self.store2, dt, 30)
        self.reservation3 = self.service._create_reservation(self.store3, dt2, 30)
        self.worker_profile.washer_profile = self.washer2_profile
        self.worker_profile.store = self.store2
        self.worker_profile.save()
        self.worker2_profile.washer_profile = self.washer2_profile
        self.worker2_profile.store = self.store3
        self.worker2_profile.save()

    def test_list(self):
        url = reverse_lazy('api:router:my_reservations-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)
        self.assertEqual(jresponse['results'][0]['pk'], self.reservation.pk)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)
        self.assertEqual(jresponse['results'][0]['pk'], self.reservation3.pk)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)
        self.assertEqual(jresponse['results'][0]['pk'], self.reservation2.pk)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker2_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)
        self.assertEqual(jresponse['results'][0]['pk'], self.reservation3.pk)

    def test_retrieve(self):
        url = reverse_lazy('api:router:my_reservations-detail', args=[self.reservation2.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker2_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['pk'], self.reservation2.pk)

    def test_disable(self):
        url = reverse_lazy('api:router:my_reservations-disable', args=[self.reservation2.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['status'], ReservationStatus.disabled.value)

        self.reservation2.status = ReservationStatus.available
        self.reservation2.save()
        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['status'], ReservationStatus.disabled.value)

    def test_cancel(self):
        url = reverse_lazy('api:router:my_reservations-cancel', args=[self.reservation2.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        self.reservation2.status = ReservationStatus.reserved
        self.reservation2.save()
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['status'], ReservationStatus.cancelled.value)

        self.reservation2.status = ReservationStatus.reserved
        self.reservation2.save()
        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['status'], ReservationStatus.cancelled.value)

    def test_start(self):
        url = reverse_lazy('api:router:my_reservations-start', args=[self.reservation2.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.reservation2.status = ReservationStatus.reserved
        self.reservation2.save()
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['status'], ReservationStatus.started.value)

        self.reservation2.status = ReservationStatus.reserved
        self.reservation2.save()
        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['status'], ReservationStatus.started.value)

    def test_complete(self):
        url = reverse_lazy('api:router:my_reservations-complete', args=[self.reservation2.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.reservation2.status = ReservationStatus.started
        self.reservation2.save()
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['status'], ReservationStatus.completed.value)

        self.reservation2.status = ReservationStatus.started
        self.reservation2.save()
        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['status'], ReservationStatus.completed.value)

