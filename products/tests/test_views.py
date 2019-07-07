import json
from decimal import Decimal
from django.test import TestCase
from rest_framework.reverse import reverse_lazy
from rest_framework import status

from base.test import BaseTestViewMixin
from cars.enums import CarType
from stores.service import StoreService
from products.service import ProductService
from products.enums import ProductType


class ProductViewSetTestView(TestCase, BaseTestViewMixin):
    def setUp(self):
        store_service = StoreService()
        self.service = ProductService()
        self.init_users()
        self.store = store_service.create_store(name="Washer1Store",
                                                washer_profile=self.washer.washer_profile,
                                                phone_number="021255", tax_office="a",
                                                tax_number="1")
        self.store2 = store_service.create_store(name="Washer2Store",
                                                washer_profile=self.washer2.washer_profile,
                                                phone_number="021255", tax_office="a",
                                                tax_number="1")
        self.product = self.service.create_product(name="Arac Parfumu", store=self.store,
                                                   washer_profile=self.washer.washer_profile)
        self.product2 = self.service.create_product(name="Arac Parfumu", store=self.store2,
                                                   washer_profile=self.washer2.washer_profile)

    def test_list(self):
        url = reverse_lazy('api:router:my_products-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 4)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)
        self.assertEqual(len(jresponse['results'][0]['productprice_set']), len(CarType.choices()))

        filtered_url = f'{url}?is_primary=true'
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(filtered_url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)
        self.assertEqual(jresponse['results'][0]['product_type'], ProductType.periodic.value)

        filtered_url = f'{url}?store={self.store.pk + 1}'
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(filtered_url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 0)

    def test_retrieve(self):
        url = reverse_lazy('api:router:my_products-detail', args=[self.product.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
        self.assertEqual(jresponse['pk'], self.product.pk)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        url = reverse_lazy('api:router:my_products-list')
        data = {
            "name": "deneme",
            "store": self.store2.pk,
            "product_type": ProductType.periodic.value,
            "is_primary": True
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        data.update({"store": self.store.pk})
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        data.update({"product_type": ProductType.other.value})
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['name'], data['name'])
        self.assertFalse(jresponse['is_primary'])
        self.assertEqual(len(jresponse['productprice_set']), len(CarType.choices()))

    def test_update(self):
        url = reverse_lazy('api:router:my_products-detail', args=[self.product.pk])
        data = {
            "pk": 57,
            "name": "İç-Dış Yıkama",
            "description": "Kullanilan malzemeler: su, sabun",
            "store": self.store2.pk,
            "is_primary": False,
            "product_type": "periodic",
            "period": 32
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
        self.assertEqual(jresponse['store'], self.product.store.pk)
        self.assertEqual(jresponse['name'], data['name'])
        self.assertEqual(jresponse['description'], data['description'])
        self.assertIsNone(jresponse['period'])
        self.assertNotEqual(jresponse['product_type'], data['product_type'])

        primary_product = self.store.get_primary_product()
        url = reverse_lazy('api:router:my_products-detail', args=[primary_product.pk])
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['store'], self.product.store.pk)
        self.assertEqual(jresponse['name'], data['name'])
        self.assertEqual(jresponse['description'], data['description'])
        self.assertEqual(jresponse['period'], data['period'])

    def test_price(self):
        url = reverse_lazy('api:router:my_products-price',
                           args=[self.product.pk, CarType.suv.value])
        data = {
            "price": Decimal('0.50')
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        data.update({"price": Decimal('40.00')})
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy(self):
        url = reverse_lazy('api:router:my_products-detail', args=[self.product.pk])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.delete(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.delete(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.delete(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.delete(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        primary_product = self.store.get_primary_product()
        url = reverse_lazy('api:router:my_products-detail', args=[primary_product.pk])
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.delete(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
