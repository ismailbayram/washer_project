import json
from model_mommy import mommy
from django.test import TestCase
from rest_framework.reverse import reverse_lazy
from rest_framework import status

from base.test import BaseTestViewMixin
from users.service import UserService


class WorkerProfileViewSetTestView(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.user_service = UserService()
        super().setUp()
        self.init_users()
        self.store = mommy.make('stores.Store', washer_profile=self.washer.washer_profile)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2.washer_profile)
        self.store3 = mommy.make('stores.Store', washer_profile=self.washer2.washer_profile)
        self.worker_profile = self.worker.worker_profile
        self.worker_profile.washer_profile = self.washer.washer_profile
        self.worker_profile.store = self.store
        self.worker_profile.save()
        self.worker2_profile = self.worker2.worker_profile
        self.worker2_profile.washer_profile = self.washer2.washer_profile
        self.worker2_profile.store = self.store2
        self.worker2_profile.save()
        self.worker3, _ = self.user_service.get_or_create_user(first_name='Ahmet',
                                                               last_name='Cetin',
                                                               phone_number='555226')
        self.worker3_profile = self.worker3.worker_profile

    def test_list(self):
        url = reverse_lazy('api:router:workers-list')

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
        self.assertEqual(jresponse['results'][0]['pk'], self.worker_profile.pk)

        url_filtered = f'{url}?store={self.store.pk}'
        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url_filtered, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)

    def test_retrieve(self):
        url = reverse_lazy('api:router:workers-detail', args=[self.worker_profile.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['pk'], self.worker_profile.pk)

    def test_create(self):
        url = reverse_lazy('api:router:workers-list')
        data = {
            "first_name": "Ahmet",
            "last_name": "Cetin",
            "phone_number": "555224",
            "store": self.store.pk
        }

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data.update({
            "first_name": self.worker3.first_name,
            "last_name": self.worker3.last_name,
            "phone_number": self.worker3.phone_number,
        })
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data.update({"store": self.store2.pk})
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_fire(self):
        url = reverse_lazy('api:router:workers-fire', args=[self.worker_profile.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_move(self):
        url = reverse_lazy('api:router:workers-move', args=[self.worker_profile.pk, self.store.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse_lazy('api:router:workers-move', args=[self.worker_profile.pk, self.store2.pk])
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse_lazy('api:router:workers-move', args=[self.worker2_profile.pk, self.store.pk])
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update(self):
        url = reverse_lazy('api:router:workers-detail', args=[self.worker_profile.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.put(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.put(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.put(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.patch(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.patch(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.patch(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.patch(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy(self):
        url = reverse_lazy('api:router:workers-detail', args=[self.worker_profile.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.delete(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
