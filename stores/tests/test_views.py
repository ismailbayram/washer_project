import json
from model_mommy import mommy
from django.test import TestCase
from rest_framework.reverse import reverse_lazy
from rest_framework import status

from base.test import BaseTestViewMixin
from stores.models import Store


class StoreViewSetTestView(TestCase, BaseTestViewMixin):
    def setUp(self):
        super().setUp()
        self.init_users()
        self.store = mommy.make('stores.Store', washer_profile=self.washer.washer_profile,
                                is_approved=False, is_active=False)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2.washer_profile,
                                 is_approved=True)

    def test_create_store(self):
        url = reverse_lazy('api:router:my_stores-list')
        data = {
            "name": "Test store",
        }

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data.update({
            "tax_office": "Tax Office",
            "tax_number": "Tax Number",
            "phone_number": "0555555"
        })
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_store(self):
        url = reverse_lazy('api:router:my_stores-detail', args=[self.store.pk])
        data = {
            "name": "Test store",
            "tax_office": self.store.tax_office,
            "tax_number": self.store.tax_number,
            "phone_number": self.store.phone_number,
        }

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['name'], data['name'])

    def test_list_stores(self):
        url = reverse_lazy('api:router:my_stores-list')

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)
        self.assertEqual(jresponse['results'][0]['name'], self.store.name)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)

    def test_retrieve_store(self):
        url = reverse_lazy('api:router:my_stores-detail', args=[self.store.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['name'], self.store.name)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['name'], self.store.name)

    def test_decline_store(self):
        url = reverse_lazy('api:router:my_stores-decline', args=[self.store2.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        store = Store.objects.get(pk=self.store2.pk)
        self.assertFalse(store.is_approved)

    def test_approve_store(self):
        url = reverse_lazy('api:router:my_stores-approve', args=[self.store.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        store = Store.objects.get(pk=self.store.pk)
        self.assertTrue(store.is_approved)

    def test_address_store(self):
        url = reverse_lazy('api:router:my_stores-address', args=[self.store.pk])
        country = mommy.make('address.Country', name="turkey")
        city = mommy.make('address.City', name="istanbul", country=country)
        township = mommy.make('address.Township', name="sisli", city=city)
        store = Store.objects.get(pk=self.store.pk)
        store.is_approved = True
        store.save()

        data = {
            "country": country.pk,
            "city": city.pk,
            "township": township.pk,
            "line": "Test Line",
            "postcode": "34220"
        }

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['country'], country.pk)
        self.assertEqual(jresponse['city'], city.pk)
        self.assertEqual(jresponse['township'], township.pk)

        store.refresh_from_db()
        self.assertEqual(store.address.pk, jresponse['pk'])
        self.assertFalse(store.is_approved)
