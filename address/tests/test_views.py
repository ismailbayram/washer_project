import json
from model_mommy import mommy
from django.test import TestCase
from rest_framework.reverse import reverse_lazy
from rest_framework import status

from address.models import (Country, City, Township)
from base.test import BaseTestViewMixin


class BaseLocationTestCase(TestCase):
    def setUp(self):
        self.country = mommy.make('address.Country', name="turkey")
        self.country2 = mommy.make('address.Country', name="valhalla")
        self.city = mommy.make('address.City', name="istanbul", country=self.country)
        self.city2 = mommy.make('address.City', name="ragnar", country=self.country2)
        self.township = mommy.make('address.Township', name="sisli", city=self.city)
        self.township2 = mommy.make('address.Township', name="valhalla merkez", city=self.city2)


class CountryViewSetTestView(BaseLocationTestCase, BaseTestViewMixin):
    def setUp(self):
        super().setUp()
        self.init_users()

    def test_list_action(self):
        url = reverse_lazy('api:router:countries-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)
        self.assertEqual(jresponse['results'][0]['pk'], self.country.pk)
        self.assertEqual(jresponse['results'][0]['name'], self.country.name)

    def test_retrieve_action(self):
        url = reverse_lazy('api:router:countries-detail', args=[self.country.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['pk'], self.country.pk)
        self.assertEqual(jresponse['name'], self.country.name)

    # def test_create_action(self):
    #     url = reverse_lazy('api:router:countries-list')
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     data = {
    #         'name': 'Russia'
    #     }
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     jresp = json.loads(response.content)
    #     country = Country.objects.get(name=data['name'])
    #     self.assertEqual(jresp['pk'], country.pk)
    #
    # def test_update_action(self):
    #     url = reverse_lazy('api:router:countries-detail', args=[self.country.pk])
    #     response = self.client.put(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     data = {
    #         'name': 'Turkiye'
    #     }
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.put(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.put(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.put(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
    #     response = self.client.put(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     jresp = json.loads(response.content)
    #     country = Country.objects.get(name=data['name'])
    #     self.assertEqual(jresp['pk'], country.pk)
    #
    # def test_destroy_action(self):
    #     url = reverse_lazy('api:router:countries-detail', args=[self.country.pk])
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     country = Country.objects.get(pk=self.country.pk)
    #     self.assertFalse(country.is_active)


class CityViewSetTestView(BaseLocationTestCase, BaseTestViewMixin):
    def setUp(self):
        super().setUp()
        self.init_users()

    def test_list_action(self):
        url = reverse_lazy('api:router:cities-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)
        self.assertEqual(jresponse['results'][0]['pk'], self.city.pk)
        self.assertEqual(jresponse['results'][0]['name'], self.city.name)

        url = f'{url}?country={self.country.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)
        self.assertEqual(jresponse['results'][0]['pk'], self.city.pk)
        self.assertEqual(jresponse['results'][0]['name'], self.city.name)

    def test_retrieve_action(self):
        url = reverse_lazy('api:router:cities-detail', args=[self.city.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['pk'], self.city.pk)
        self.assertEqual(jresponse['name'], self.city.name)

    # def test_create_action(self):
    #     url = reverse_lazy('api:router:cities-list')
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     data = {
    #         'name': 'Balikesir',
    #         'country': self.country.pk
    #     }
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     jresp = json.loads(response.content)
    #     city = City.objects.get(name=data['name'])
    #     self.assertEqual(jresp['pk'], city.pk)
    #
    # def test_update_action(self):
    #     url = reverse_lazy('api:router:cities-detail', args=[self.city.pk])
    #     response = self.client.patch(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     data = {
    #         'name': 'Balikesir ili'
    #     }
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.patch(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.patch(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.patch(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
    #     response = self.client.patch(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     jresp = json.loads(response.content)
    #     city = City.objects.get(name=data['name'])
    #     self.assertEqual(jresp['pk'], city.pk)
    #
    # def test_destroy_action(self):
    #     url = reverse_lazy('api:router:cities-detail', args=[self.city.pk])
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     city = City.objects.get(pk=self.city.pk)
    #     self.assertFalse(city.is_active)


class TownshipViewSetTestView(BaseLocationTestCase, BaseTestViewMixin):
    def setUp(self):
        super().setUp()
        self.init_users()

    def test_list_action(self):
        url = reverse_lazy('api:router:townships-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)
        self.assertEqual(jresponse['results'][0]['pk'], self.township.pk)
        self.assertEqual(jresponse['results'][0]['name'], self.township.name)

        url = f'{url}?city={self.city.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)
        self.assertEqual(jresponse['results'][0]['pk'], self.township.pk)
        self.assertEqual(jresponse['results'][0]['name'], self.township.name)

    def test_retrieve_action(self):
        url = reverse_lazy('api:router:townships-detail', args=[self.township.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['pk'], self.township.pk)
        self.assertEqual(jresponse['name'], self.township.name)

    # def test_create_action(self):
    #     url = reverse_lazy('api:router:townships-list')
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     data = {
    #         'name': 'Esenler',
    #         'city': self.city.pk
    #     }
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
    #     response = self.client.post(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     jresp = json.loads(response.content)
    #     township = Township.objects.get(name=data['name'])
    #     self.assertEqual(jresp['pk'], township.pk)
    #
    # def test_update_action(self):
    #     url = reverse_lazy('api:router:townships-detail', args=[self.township.pk])
    #     response = self.client.patch(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     data = {
    #         'name': 'Sisli ilcesi'
    #     }
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.patch(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.patch(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.patch(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
    #     response = self.client.patch(url, data=data, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     jresp = json.loads(response.content)
    #     township = Township.objects.get(name=data['name'])
    #     self.assertEqual(jresp['pk'], township.pk)
    #
    # def test_destroy_action(self):
    #     url = reverse_lazy('api:router:townships-detail', args=[self.township.pk])
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
    #     response = self.client.delete(url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     township = Township.objects.get(pk=self.township.pk)
    #     self.assertFalse(township.is_active)
