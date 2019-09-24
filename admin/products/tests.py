from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse_lazy

from model_mommy import mommy
from base.test import BaseTestViewMixin


class ProductPriceViewSetTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.init_users()
        self.product_price = mommy.make('products.ProductPrice')

    def test_retrieve_product_price(self):
        url = reverse_lazy('admin_api:router:product_prices-detail', args=[self.product_price.pk])
        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_product_prices(self):
        url = reverse_lazy('admin_api:router:product_prices-list')
        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
