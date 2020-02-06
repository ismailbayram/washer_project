import time

from django.test import TestCase
from django.utils import timezone
from elasticsearch import NotFoundError
from model_mommy import mommy

from base.test import BaseTestViewMixin
from notifications.enums import NotificationType
from notifications.models import Notification
from reservations.enums import ReservationStatus
from search.documents import StoreDoc
from search.indexer import StoreIndexer
from stores.models import Store
from stores.tasks import delete_store_index, notify_stores_for_increasing


class StoreTaskTest(TestCase, BaseTestViewMixin):

    def setUp(self):
        store_config_data = {
            "reservation_hours": {
                "monday": {
                    "start": "09:00",
                    "end": "10:00"
                },
                "tuesday": {
                    "start": "09:00",
                    "end": "10:00"
                },
            }
        }
        self.init_users()
        self.address1 = mommy.make('address.Address')
        self.address2 = mommy.make('address.Address')
        self.store1 = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                 is_approved=True, is_active=True, address=self.address1,
                                 latitude=35, longitude=34, phone_number="+905388197550",
                                 config=store_config_data)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=True, is_active=True, address=self.address2,
                                 latitude=35, longitude=34, phone_number="+905388197550",
                                 config=store_config_data)
        self.product1 = mommy.make('products.Product', is_primary=True,
                                   is_active=True, period=60, store=self.store1)
        self.product2 = mommy.make('products.Product', is_primary=True,
                                   is_active=True, period=60, store=self.store2)
        self.store_indexer = StoreIndexer()
        mommy.make('reservations.Reservation', status=ReservationStatus.reserved,
                   start_datetime=timezone.now(), store=self.store1)
        mommy.make('reservations.Reservation', status=ReservationStatus.reserved,
                   start_datetime=timezone.now(), store=self.store1)

    def test_notify_stores_for_increasing_task(self):
        notify_stores_for_increasing()
        notifications = Notification.objects.filter(notification_type=NotificationType.so_reservation_want_increase).all()
        time.sleep(1)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].data['store_id'], self.store1.id)

    def test_delete_store_index(self):
        self.store_indexer.index_store(self.store1)
        with self.assertRaises(Store.DoesNotExist):
            delete_store_index(store_id=111111)

        delete_store_index(self.store1.id)
        with self.assertRaises(NotFoundError):
            StoreDoc().get(id=self.store1.pk)
