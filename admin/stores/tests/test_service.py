from django.test import TestCase
from model_mommy import mommy

from base.test import BaseTestViewMixin
from notifications.enums import NotificationType
from admin.stores.exceptions import (StoreIsAlreadyApproved,
                                     StoreIsAlreadyDeclined)
from admin.stores.service import AdminStoreService


class StoreAdminServiceTest(BaseTestViewMixin, TestCase):
    def setUp(self):
        self.service = AdminStoreService()
        self.init_users()
        self.store = mommy.make(
            'stores.Store', is_approved=True, phone_number="05555555555")
        self.washers_store = mommy.make('stores.Store', is_approved=True,
                                        phone_number="05555555555",
                                        washer_profile=self.washer_profile)

    def test_approve(self):
        store = mommy.make('stores.Store', is_approved=False)
        store = self.service.approve_store(store)
        self.assertTrue(store.is_approved)

        # START notif test
        self.assertEqual(store.washer_profile.notifications.count(), 1)
        self.assertEqual(
            store.washer_profile.notifications.last().notification_type,
            NotificationType.store_approved
        )
        # END notif test

        with self.assertRaises(StoreIsAlreadyApproved):
            self.service.approve_store(store)

    def test_decline(self):
        store = mommy.make('stores.Store', is_approved=True)
        store = self.service.decline_store(store)
        self.assertFalse(store.is_approved)

        with self.assertRaises(StoreIsAlreadyDeclined):
            self.service.decline_store(store)
