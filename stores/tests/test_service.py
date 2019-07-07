from model_mommy import mommy

from django.test import TestCase

from base.test import BaseTestViewMixin
from stores.service import StoreService
from cars.enums import CarType


class StoreServiceTest(BaseTestViewMixin, TestCase):
    def setUp(self):
        self.service = StoreService()
        self.init_users()
        self.store = mommy.make('stores.Store', is_approved=True, phone_number="05555555555")

    def test_create_store(self):
        data = {
            "name": "Test Store",
            "washer_profile": self.washer.washer_profile,
            "phone_number": "05555555555",
            "tax_office": "Tax Office",
            "tax_number": "000111222",
            "latitude": None,
            "longitude": None,
        }

        store = self.service.create_store(**data)
        self.assertEqual(store.name, data['name'])
        self.assertEqual(store.washer_profile, data['washer_profile'])
        self.assertEqual(store.latitude, data['latitude'])
        self.assertTrue(store.is_active)
        self.assertFalse(store.is_approved)
        self.assertEqual(store.config, {'opening_hours': {}, 'reservation_hours': {}})

        self.assertEqual(store.product_set.count(), 1)
        self.assertEqual(store.product_set.filter(is_primary=True).count(), 1)
        primary_product = store.product_set.first()
        self.assertEqual(primary_product.productprice_set.count(), len(CarType.choices()))

    def test_update_store(self):
        data = {
            "name": "Test Updated",
            "phone_number": "05555555555",
            "tax_office": "Tax Office",
            "tax_number": "000111222",
        }

        store = self.service.update_store(self.store, **data)
        self.assertEqual(store.name, data['name'])
        self.assertEqual(store.phone_number, data['phone_number'])
        self.assertTrue(store.is_approved)

        data.update({
            "phone_number": "05555555551",
        })

        store = self.service.update_store(self.store, **data)
        self.assertEqual(store.phone_number, data['phone_number'])
        self.assertFalse(store.is_approved)

        data.update({
            "is_active": False
        })

        store = self.service.update_store(self.store, **data)
        self.assertFalse(store.is_active)

        self.store.refresh_from_db()
        self.store.is_approved = True
        self.store.save()
        data.update({
            "latitude": 42.00,
            "longitude": 36.00
        })
        store = self.service.update_store(self.store, **data)
        self.assertEqual(store.latitude, data['latitude'])
        self.assertEqual(store.longitude, data['longitude'])
        self.assertFalse(store.is_approved)

    def test_approve(self):
        store = mommy.make('stores.Store', is_approved=False)
        store = self.service.approve_store(store)
        self.assertTrue(store.is_approved)

    def test_decline(self):
        store = mommy.make('stores.Store', is_approved=True)
        store = self.service.decline_store(store)
        self.assertFalse(store.is_approved)

