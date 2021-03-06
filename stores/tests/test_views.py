import json
import os

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

        path = os.path.join(settings.BASE_DIR, 'stores/tests/img.txt')
        with open(path, 'r') as file:
            self.photo = file.read()

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
            "phone_number": "+905388197550"
        })
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_store_phone_valid_test(self):
        url = reverse_lazy('api:router:my_stores-list')
        phones = {
            "+902128171779": True,
            "+905388197555": True,
            "+908388197555": True,
            "+903881975009": True,
            "+95388197550": False,
            "+90538819755": False,
            "+953881975500": False,
            "+9O3881975500": False,
        }

        data = {
            "name": "Test store",
        }

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}

        for phone, expected_response in phones.items():
            data.update({
                "tax_office": "Tax Office",
                "tax_number": "Tax Number",
                "phone_number": phone
            })

            response = self.client.post(url, data=data, content_type='application/json', **headers)
            if expected_response:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            else:
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['name'], data['name'])

        data.update({
            'payment_options': {
                'credit_card': True,
                'cash': True
            }
        })
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertTrue(jresponse['payment_options']['credit_card'])
        self.assertTrue(jresponse['payment_options']['cash'])

        data.update({
            'payment_options': {
                'credit_card': False,
                'cash': False
            }
        })
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_logo_add_and_delete(self):
        logo_url = reverse_lazy('api:router:my_stores-logo', args=[self.store.pk])
        store_url = reverse_lazy('api:router:my_stores-detail', args=[self.store.pk])
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}

        data ={
            "logo": self.photo
        }

        # save image
        image_response = self.client.post(logo_url, data=data, content_type='application/json', **headers)
        self.assertEqual(image_response.status_code, status.HTTP_202_ACCEPTED)

        # get image
        store_response = self.client.get(store_url, content_type='application/json', **headers)
        url = store_response.data.get('logo')
        self.assertNotEqual(url, None)

        # delete image
        image_response = self.client.delete(logo_url, content_type='application/json', **headers)
        self.assertEqual(image_response.status_code, status.HTTP_202_ACCEPTED)

        # cant add or delete image washer2 or customer
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(logo_url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(logo_url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(logo_url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(logo_url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_gallery(self):
        url = reverse_lazy('api:router:my_stores-add-image', args=[self.store.pk])
        store_url = reverse_lazy('api:router:my_stores-detail', args=[self.store.pk])
        data ={
            "image": self.photo
        }
        # cant send image by anouther
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # get image from store
        store_response = self.client.get(store_url, content_type='application/json', **headers)
        image_pk = store_response.data.get('images')[0].get('pk')

        # delete test with washer2 and customer
        delete_url = reverse_lazy('api:router:my_stores-delete-image', args=[self.store.pk, image_pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.delete(delete_url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.delete(delete_url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


        # delete test with owner
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        delete_url = reverse_lazy('api:router:my_stores-delete-image', args=[self.store.pk, image_pk])
        response = self.client.delete(delete_url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)


class StoreDetailViewTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        super().setUp()
        self.init_users()
        self.address = mommy.make('address.Address')
        self.address2 = mommy.make('address.Address')
        self.store = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                is_approved=False, is_active=False, address=self.address,
                                latitude=35, longitude=34)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=True, address=self.address2,
                                latitude=35, longitude=34)

    def test_detail(self):
        url = reverse_lazy('api:store_detail', args=[self.store.pk])

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse_lazy('api:store_detail', args=[self.store2.pk])
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
