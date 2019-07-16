from model_mommy import mommy
from decimal import Decimal
from django.test import TestCase, override_settings

from base.test import BaseTestViewMixin
from stores.exceptions import StoreDoesNotBelongToWasherException
from cars.enums import CarType
from products.models import ProductPrice
from products.service import ProductService, PRIMARY_PRODUCT
from products.enums import ProductType
from products.exceptions import (PeriodIsRequiredException,
                                 ProductPriceCanNotLessThanException,
                                 PrimaryProductsCanNotDeletedException)


class ProductServiceTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.init_users()
        self.service = ProductService()
        self.store = mommy.make('stores.Store', washer_profile=self.washer.washer_profile)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2.washer_profile)

    def test_create(self):
        data = {
            "name": "Arac Parfumu",
            "store": self.store2,
            "washer_profile": self.washer.washer_profile,
            "period": None,
            "product_type": ProductType.periodic,
            "description": "Description"
        }

        with self.assertRaises(PeriodIsRequiredException):
            self.service.create_product(**data)

        data.update({"product_type": ProductType.other})
        with self.assertRaises(StoreDoesNotBelongToWasherException):
            self.service.create_product(**data)

        data.update({"store": self.store})
        product = self.service.create_product(**data)
        self.assertFalse(product.is_primary)
        self.assertEqual(product.name, data['name'])
        self.assertEqual(product.period, data['period'])
        self.assertEqual(product.store, data['store'])
        self.assertEqual(product.washer_profile, data['washer_profile'])
        self.assertEqual(product.productprice_set.count(), len(CarType.choices()))

    def test_create_primary(self):
        product = self.service.create_primary_product(store=self.store)
        self.assertTrue(product.is_primary)
        self.assertEqual(product.product_type, ProductType.periodic)
        self.assertEqual(product.period, PRIMARY_PRODUCT['period'])

    @override_settings(DEFAULT_PRODUCT_PRICE=Decimal('15.00'))
    def test_create_productprice_set(self):
        product = mommy.make('products.Product')
        self.service._create_productprice_set(product)
        queryset = ProductPrice.objects.filter(product=product)
        self.assertEqual(queryset.count(), len(CarType.choices()))
        self.assertEqual(queryset.first().price, Decimal('15.00'))

    def test_update_price(self):
        product = mommy.make('products.Product')
        self.service._create_productprice_set(product)
        queryset = ProductPrice.objects.filter(product=product)
        suv_price = queryset.get(car_type=CarType.suv)
        with self.assertRaises(ProductPriceCanNotLessThanException):
            self.service.update_price(suv_price, Decimal('0.45'))

        suv_price = self.service.update_price(suv_price, Decimal('22.00'))
        self.assertEqual(suv_price.price, Decimal('22.00'))

    def test_update_product(self):
        product = mommy.make('products.Product', product_type=ProductType.other)
        data = {
            "name": "Updated Name",
            "description": "Updated Description",
            "store": 1,
            "washer_profile": 3,
            "product_type": ProductType.periodic,
            "period": 32
        }
        product = self.service.update_product(product, **data)
        self.assertEqual(product.name, data['name'])
        self.assertEqual(product.description, data['description'])
        self.assertNotEqual(product.store, data['store'])
        self.assertNotEqual(product.washer_profile, data['washer_profile'])
        self.assertNotEqual(product.product_type, data['product_type'])
        self.assertNotEqual(product.period, data['period'])

        product = mommy.make('products.Product', product_type=ProductType.periodic, period=45)
        data.update({
            "period": 45
        })
        product = self.service.update_product(product, **data)
        self.assertEqual(product.name, data['name'])
        self.assertEqual(product.description, data['description'])
        self.assertNotEqual(product.store, data['store'])
        self.assertNotEqual(product.washer_profile, data['washer_profile'])
        self.assertEqual(product.product_type, data['product_type'])
        self.assertEqual(product.period, data['period'])

    def test_delete_product(self):
        product = self.service.create_primary_product(self.store)

        with self.assertRaises(PrimaryProductsCanNotDeletedException):
            self.service.delete_product(product)

        product = self.service.create_product(name="test", store=self.store,
                                              washer_profile=self.store.washer_profile)

        product = self.service.delete_product(product)
        product.refresh_from_db()
        self.assertFalse(product.is_active)
