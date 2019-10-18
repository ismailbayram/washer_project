from django.conf import settings
from django.test import TestCase
from model_mommy import mommy
from rest_framework import status
from rest_framework.reverse import reverse_lazy

from base.test import BaseTestViewMixin
from stores.models import Store


class StoreViewSetTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        super().setUp()
        self.init_users()
        self.address = mommy.make('address.Address')
        self.address2 = mommy.make('address.Address')
        self.store = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                is_approved=False, is_active=False, address=self.address,
                                latitude=35, longitude=34, phone_number="+905388197550")
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=True, address=self.address2,
                                 latitude=35, longitude=34)

    def test_approve_store(self):
        url = reverse_lazy('admin_api:router:stores-approve',
                           args=[self.store.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(
            url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(
            url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(
            url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.post(
            url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        store = Store.objects.get(pk=self.store.pk)
        self.assertTrue(store.is_approved)

    def test_decline_store(self):
        url = reverse_lazy('admin_api:router:stores-decline',
                           args=[self.store2.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(
            url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(
            url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(
            url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.post(
            url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        store = Store.objects.get(pk=self.store2.pk)
        self.assertFalse(store.is_approved)

    # def test_activate_store(self):
    #     url = reverse_lazy('admin_api:router:stores-activate',
    #                        args=[self.store.pk])

    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.post(
    #         url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.post(
    #         url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.post(
    #         url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     store = Store.objects.get(pk=self.store.pk)
    #     self.assertTrue(store.is_active)

    # def test_deactivate_store(self):
    #     url = reverse_lazy('admin_api:router:stores-deactivate',
    #                        args=[self.store.pk])

    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
    #     response = self.client.post(
    #         url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
    #     response = self.client.post(
    #         url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
    #     response = self.client.post(
    #         url, content_type='application/json', **headers)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     store = Store.objects.get(pk=self.store.pk)
    #     self.assertFalse(store.is_active)
