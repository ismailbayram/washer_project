import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase
from model_mommy import mommy

from base.test import BaseTestViewMixin
from base.utils import thumbnail_file_name_by_orginal_name
from cars.enums import CarType
from stores.service import StoreService


class StoreServiceTest(BaseTestViewMixin, TestCase):
    def setUp(self):
        self.service = StoreService()
        self.init_users()
        self.store = mommy.make('stores.Store', is_approved=True, phone_number="05555555555")
        self.washers_store = mommy.make('stores.Store', is_approved=True,
                                        phone_number="05555555555",
                                        washer_profile=self.washer_profile)

        path = os.path.join(settings.BASE_DIR, 'stores/tests/img.jpeg')
        with open(path, mode='rb') as file:
            self.photo = file.read()

    def test_create_store(self):
        data = {
            "name": "Test Store",
            "washer_profile": self.washer_profile,
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

    def test_active(self):
        store = mommy.make('stores.Store', is_active=False)
        store = self.service.activate_store(store)
        self.assertTrue(store.is_active)

    def test_deactivate(self):
        store = mommy.make('stores.Store', is_active=True)
        store = self.service.deactivate_store(store)
        self.assertFalse(store.is_active)

    def test_add_delete_logo(self):
        content_file_logo = ContentFile(self.photo)
        content_file_logo.name = "img.jpeg"

        store = self.service.add_logo(store=self.washers_store, logo=content_file_logo)
        file_name = store.logo.name
        self.assertTrue(default_storage.exists(file_name))

        self.service.delete_logo(store)
        self.assertFalse(default_storage.exists(file_name))


    def test_add_delete_image(self):
        content_file_logo = ContentFile(self.photo)
        content_file_logo.name = "img.jpeg"

        self.service.add_image(store=self.washers_store, image=content_file_logo,
                               washer_profile=self.washer_profile)

        file_name = self.washers_store.images.first().image.name
        self.assertTrue(default_storage.exists(file_name))
        for size_name in settings.IMAGE_SIZES.keys():
            thumb_f_n = thumbnail_file_name_by_orginal_name(file_name, size_name)
            self.assertTrue(default_storage.exists(thumb_f_n))

        self.service.delete_image(self.washers_store.images.first(), self.washer_profile)

        self.assertFalse(default_storage.exists(file_name))
        for size_name in settings.IMAGE_SIZES.keys():
            thumb_f_n = thumbnail_file_name_by_orginal_name(file_name, size_name)
            self.assertFalse(default_storage.exists(thumb_f_n))
