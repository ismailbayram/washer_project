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
            "notification_type": NotificationType.you_fired.value,
            "data": {"bir": "haha", "iki": "ha?", 'view': 'naber', 'view_id': '24'},
            "receiver": self.washer.washer_profile
        }
        self.service._create_notification(**create_data)

        db_notif = Notification.objects.last()
        self.assertEqual(db_notif.notification_type.value, create_data['notification_type'])
        self.assertEqual(db_notif.data, create_data['data'])
        self.assertEqual(db_notif.content_object, create_data['receiver'])

        create_data['receiver'] = self.customer.customer_profile
        self.service._create_notification(**create_data)
        db_notif = self.customer.customer_profile.notifications.first()

        self.assertEqual(db_notif.notification_type.value, create_data['notification_type'])
        self.assertEqual(db_notif.data, create_data['data'])
        self.assertEqual(db_notif.content_object, create_data['receiver'])

        create_data['receiver'] = self.worker.worker_profile
        self.service._create_notification(**create_data)
        db_notif = self.worker.worker_profile.notifications.first()

        self.assertEqual(db_notif.notification_type.value, create_data['notification_type'])
        self.assertEqual(db_notif.data, create_data['data'])
        self.assertEqual(db_notif.content_object, create_data['receiver'])


        # Test store
        create_data['receiver'] = self.store
        create_data['data']['view'] = "store2"
        create_data['data']['view_id'] = "15"
        self.service._create_notification(**create_data)

        self.assertEqual(self.washer.washer_profile.notifications.count(), 2)
        self.assertEqual(self.worker.worker_profile.notifications.count(), 2)
        self.assertEqual(self.worker2.worker_profile.notifications.count(), 1)

        self.assertEqual(self.washer.washer_profile.notifications.first().data['view'], 'store2')
        self.assertEqual(self.worker2.worker_profile.notifications.first().data['view_id'], '15')

    def test_send_notification(self):
        self.service.send(instance=self.worker_profile,
                                notif_type=NotificationType.reservation_started,
                                to=self.washer_profile)
        self.assertEqual(self.washer_profile.notifications.count(), 1)
        self.assertEqual(self.washer_profile.notifications.last().notification_type,
                         NotificationType.reservation_started)


        self.service.send(instance=self.worker_profile,
                                notif_type=NotificationType.reservation_canceled,
                                to=self.store)
        self.assertEqual(self.washer_profile.notifications.count(), 2)
        self.assertEqual(self.washer_profile.notifications.first().notification_type,
                         NotificationType.reservation_canceled)
        self.assertEqual(self.worker_profile.notifications.count(), 1)
        self.assertEqual(self.worker_profile.notifications.first().notification_type,
                         NotificationType.reservation_canceled)

        self.service.send(instance=self.worker_profile,
                                notif_type=NotificationType.reservation_started,
                                to=self.washer_profile)
        self.assertEqual(self.washer_profile.notifications.count(), 3)
