from model_mommy import mommy
from decimal import Decimal
from django.test import TestCase, override_settings

from base.test import BaseTestViewMixin
from cars.enums import CarType
from cars.service import CarService
from cars.exceptions import CustomerHasNoSelectedCarException
from products.service import ProductService
from baskets.models import Basket
from baskets.service import BasketService
from baskets.enums import BasketStatus
from baskets.exceptions import (PrimaryProductsQuantityMustOne,
                                BasketInvalidException,
                                BasketEmptyException)


@override_settings(DEFAULT_PRODUCT_PRICE=Decimal('20.00'))
class BasketServiceTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.service = BasketService()
        self.product_service = ProductService()
        self.car_service = CarService()
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

    def test_get_or_create_basket(self):
        basket = self.service.get_or_create_basket(customer_profile=self.customer_profile)
        self.assertEqual(basket.status, BasketStatus.active)
        self.assertEqual(basket.get_total_amount(), Decimal('0.00'))
        self.assertEqual(basket.get_total_quantity(), 0)
        self.assertTrue(basket.is_empty)
        self.assertEqual(basket.car, self.car)

        basket = self.service.get_or_create_basket(customer_profile=self.customer_profile)
        self.assertEqual(Basket.objects.filter(customer_profile=self.customer_profile).count(), 1)

        basket.delete()
        self.car.delete()
        with self.assertRaises(CustomerHasNoSelectedCarException):
            self.service.get_or_create_basket(customer_profile=self.customer_profile)

    def test_add_basket_item(self):
        basket = self.service.get_or_create_basket(customer_profile=self.customer_profile)

        self.service.add_basket_item(basket, self.product1)
        self.assertEqual(basket.get_total_quantity(), 1)
        self.assertEqual(basket.get_total_amount(), Decimal('20.00'))
        self.assertFalse(basket.is_empty)

        with self.assertRaises(PrimaryProductsQuantityMustOne):
            self.service.add_basket_item(basket, self.product1)

        self.service.add_basket_item(basket, self.product2)
        self.assertEqual(basket.get_total_quantity(), 2)
        self.assertEqual(basket.get_total_amount(), Decimal('40.00'))

        self.service.add_basket_item(basket, self.product2)
        self.assertEqual(basket.get_total_quantity(), 3)
        self.assertEqual(basket.get_total_amount(), Decimal('60.00'))

        self.service.add_basket_item(basket, self.product3)
        self.assertEqual(basket.get_total_quantity(), 1)
        self.assertEqual(basket.get_total_amount(), Decimal('20.00'))

    def test_clean_basket(self):
        basket = self.service.get_or_create_basket(customer_profile=self.customer_profile)
        self.service.add_basket_item(basket, self.product1)
        self.service.add_basket_item(basket, self.product2)
        self.service.add_basket_item(basket, self.product2)

        self.service.clean_basket(basket)
        self.assertEqual(basket.get_total_quantity(), 0)
        self.assertEqual(basket.get_total_amount(), Decimal('0.00'))
        self.assertTrue(basket.is_empty)

    def test_delete_basket_item(self):
        basket = self.service.get_or_create_basket(customer_profile=self.customer_profile)
        self.service.add_basket_item(basket, self.product1)
        self.service.add_basket_item(basket, self.product2)
        self.service.add_basket_item(basket, self.product2)

        self.service.delete_basket_item(basket, self.product2)
        self.assertEqual(basket.get_total_quantity(), 1)
        self.assertEqual(basket.get_total_amount(), Decimal('20.00'))

    def test_complete_basket(self):
        basket = self.service.get_or_create_basket(customer_profile=self.customer_profile)
        with self.assertRaises(BasketEmptyException):
            self.service.complete_basket(basket)

        self.service.add_basket_item(basket, self.product1)
        self.service.add_basket_item(basket, self.product2)
        self.service.add_basket_item(basket, self.product2)

        self.service.complete_basket(basket)
        self.assertEqual(basket.status, BasketStatus.completed)

        for bi in basket.basketitem_set.all():
            self.assertIsNotNone(bi.amount)

        self.product_service.delete_product(self.product2)

        with self.assertRaises(BasketInvalidException):
            self.service.complete_basket(basket)
