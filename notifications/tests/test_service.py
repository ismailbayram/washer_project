from django.test import TestCase
from model_mommy import mommy

from base.test import BaseTestViewMixin
from notifications.enums import NotificationType
from notifications.models import Notification
from notifications.service import NotificationService


class NotificationTest(BaseTestViewMixin, TestCase):
    def setUp(self):
        self.init_users()
        self.service = NotificationService()

        self.store = mommy.make('stores.Store', is_approved=True, phone_number="05555555555")
        self.store.washer_profile = self.washer_profile
        self.store.save()
        self.worker_profile.store = self.store
        self.worker_profile.save()
        self.worker2_profile.store = self.store
        self.worker2_profile.save()

    def test_create_notification(self):
        create_data = {
            "notification_type": NotificationType.reservation_started.value,
            "data": {"bir": "haha", "iki": "ha?"},
            "view": "store",
            "view_id": "1",
            "receiver": self.washer.washer_profile
        }
        self.service.create_notification(**create_data)

        db_notif = Notification.objects.last()
        self.assertEqual(db_notif.notification_type.value, create_data['notification_type'])
        self.assertEqual(db_notif.data, create_data['data'])
        self.assertEqual(db_notif.view, create_data['view'])
        self.assertEqual(db_notif.view_id, create_data['view_id'])
        self.assertEqual(db_notif.content_object, create_data['receiver'])

        create_data['receiver'] = self.customer.customer_profile
        self.service.create_notification(**create_data)
        db_notif = self.customer.customer_profile.notifications.first()

        self.assertEqual(db_notif.notification_type.value, create_data['notification_type'])
        self.assertEqual(db_notif.data, create_data['data'])
        self.assertEqual(db_notif.view, create_data['view'])
        self.assertEqual(db_notif.view_id, create_data['view_id'])
        self.assertEqual(db_notif.content_object, create_data['receiver'])

        create_data['receiver'] = self.worker.worker_profile
        self.service.create_notification(**create_data)
        db_notif = self.worker.worker_profile.notifications.first()

        self.assertEqual(db_notif.notification_type.value, create_data['notification_type'])
        self.assertEqual(db_notif.data, create_data['data'])
        self.assertEqual(db_notif.view, create_data['view'])
        self.assertEqual(db_notif.view_id, create_data['view_id'])
        self.assertEqual(db_notif.content_object, create_data['receiver'])


        # Test store
        create_data['receiver'] = self.store
        create_data['view'] = "store2"
        create_data['view_id'] = "15"
        self.service.create_notification(**create_data)

        self.assertEqual(self.washer.washer_profile.notifications.count(), 2)
        self.assertEqual(self.worker.worker_profile.notifications.count(), 2)
        self.assertEqual(self.worker2.worker_profile.notifications.count(), 1)

        self.assertEqual(self.washer.washer_profile.notifications.first().view, 'store2')
        self.assertEqual(self.worker2.worker_profile.notifications.first().view_id, '15')
