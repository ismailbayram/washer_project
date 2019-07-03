import json
from model_mommy import mommy
from django.test import TestCase
from rest_framework.reverse import reverse_lazy, reverse
from rest_framework import status

from users.models import User
from cars.models import (Car)
from cars.enums import CarType
from cars.service import CarService
from base.test import BaseTestViewMixin


class CarViewSetTest(BaseTestViewMixin, TestCase):
    def setUp(self):
        self.init_users()
        self.car1 = mommy.make(
            'cars.Car',
            licence_plate="09 TK 40",
            car_type = CarType.normal,
            customer_profile = self.customer.customer_profile
        )
        self.car2 = mommy.make(
            'cars.Car',
            licence_plate="09 TK 41",
            car_type = CarType.normal,
        )

    def test_list_action(self):
        url = reverse_lazy('api:router:cars-list')

        # Unauthorized get
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authorized get
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_action(self):
        url = reverse_lazy('api:router:cars-list')
        test_licence_plate = "09 DN 01"
        test_car_type = 'normal'
        data = {
            'licence_plate': test_licence_plate,
            'car_type': test_car_type,
        }

        # can't create by anonym user
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # cant create by washer
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # create by customer
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['licence_plate'], data['licence_plate'])
        self.assertEqual(response.data['car_type'], data['car_type'])

        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['licence_plate'], test_licence_plate)
        self.assertEqual(jresponse['car_type'], test_car_type)


    def test_retrieve_action(self):
        url = reverse_lazy('api:router:cars-detail', args=[self.car1.pk])

        # can't get by anonym
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # get by cutomer
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['licence_plate'], self.car1.licence_plate)

        # get by washer
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['licence_plate'], self.car1.licence_plate)


    def test_update_action(self):
        url = reverse_lazy('api:router:cars-detail', args=[self.car1.pk])
        data = {
            'licence_plate': '01 ADN 01'
        }

        # cant update anonym
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # can update by customer his car
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.patch(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.data['licence_plate'], '01 ADN 01')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # can't update by customer by not his car
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer2_token}'}
        response = self.client.patch(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # can't update by washer
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.patch(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_action(self):
        url = reverse_lazy('api:router:cars-detail', args=[self.car1.pk])

        # cant delete by anonym
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # cant delete by not owner
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer2_token}'}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # cant delete by washer
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # can delete by owner
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}

        # before deletetion we can get
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # delete
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # after deletion we can't get
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class CarSelectViewSetTest(BaseTestViewMixin, TestCase):
    def setUp(self):
        self.init_users()
        self.car1 = mommy.make(
            'cars.Car',
            licence_plate="09 TK 00",
            car_type = CarType.normal,
            customer_profile = self.customer.customer_profile
        )
        self.car2 = mommy.make(
            'cars.Car',
            licence_plate="09 TK 01",
            car_type = CarType.normal,
            customer_profile = self.customer.customer_profile
        )
        self.car3 = mommy.make(
            'cars.Car',
            licence_plate="09 TK 02",
            car_type = CarType.normal,
            customer_profile = self.customer.customer_profile
        )
        self.car4 = mommy.make(
            'cars.Car',
            licence_plate="09 TK 03",
            car_type = CarType.normal,
            customer_profile = self.customer.customer_profile
        )

    def test_destroy_action(self):
        # selected of 1 an 2 will false
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}

        url = reverse_lazy('api:router:cars-detail', args=[self.car1.pk])
        response = self.client.get(url, **headers)
        self.assertEqual(response.data['is_selected'], False)

        url = reverse_lazy('api:router:cars-detail', args=[self.car2.pk])
        response = self.client.get(url, **headers)
        self.assertEqual(response.data['is_selected'], False)

        # i will select 1 and will selected
        url = reverse_lazy('api:car_select', args=[self.car1.pk])
        response = self.client.get(str(url), **headers)
        self.assertEqual(response.data['is_selected'], True)

        url = reverse_lazy('api:router:cars-detail', args=[self.car1.pk])
        response = self.client.get(url, **headers)
        self.assertEqual(response.data['is_selected'], True)

        # 2 have to be un selected
        url = reverse_lazy('api:router:cars-detail', args=[self.car2.pk])
        response = self.client.get(url, **headers)
        self.assertEqual(response.data['is_selected'], False)

        # i will select 2 and will selected
        url = reverse_lazy('api:car_select', args=[self.car2.pk])
        response = self.client.get(str(url), **headers)
        self.assertEqual(response.data['is_selected'], True)

        url = reverse_lazy('api:router:cars-detail', args=[self.car2.pk])
        response = self.client.get(url, **headers)
        self.assertEqual(response.data['is_selected'], True)

        # 1 have to be un selected
        url = reverse_lazy('api:router:cars-detail', args=[self.car1.pk])
        response = self.client.get(url, **headers)
        self.assertEqual(response.data['is_selected'], False)
