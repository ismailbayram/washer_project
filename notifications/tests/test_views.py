from django.test import TestCase
from model_mommy import mommy
from rest_framework import status
from rest_framework.reverse import reverse_lazy

from base.test import BaseTestViewMixin
from notifications.enums import NotificationType
from notifications.service import NotificationService


class StoreViewSetTestView(TestCase, BaseTestViewMixin):
    def setUp(self):
        super().setUp()
        self.init_users()
        self.notif_service = NotificationService()

        self.store = mommy.make('stores.Store', is_approved=True, phone_number="05555555555")
        self.store.washer_profile = self.washer_profile
        self.store.save()
        self.worker_profile.store = self.store
        self.worker_profile.save()
        self.worker2_profile.store = self.store
        self.worker2_profile.save()

        self.washer_headers = {
            'HTTP_AUTHORIZATION': f'Token {self.washer_token}',
            'HTTP_X_PROFILE_TYPE': f'washer',
        }
        self.washer2_headers = {
            'HTTP_AUTHORIZATION': f'Token {self.washer2_token}',
            'HTTP_X_PROFILE_TYPE': f'washer',
        }
        self.customer_headers = {
            'HTTP_AUTHORIZATION': f'Token {self.customer_token}',
            'HTTP_X_PROFILE_TYPE': f'customer',
        }
        self.worker_headers = {
            'HTTP_AUTHORIZATION': f'Token {self.worker_token}',
            'HTTP_X_PROFILE_TYPE': f'worker',
        }

    def test_get_notifications(self):
        url = reverse_lazy('api:router:notifications-list')

        create_data = {
            "notification_type": NotificationType.you_fired.value,
            "data": {"bir": "haha", "worker_name": "ha?", "view": "/profile", "view_id": "1"},
            "receiver": self.washer.washer_profile
        }


        # Create 2 notification and retrive test
        self.notif_service._create_notification(**create_data)
        create_data['data']["view"] = 'sotre2'
        self.notif_service._create_notification(**create_data)

        response = self.client.get(url, content_type='application/json', **self.washer_headers)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['data']['view_id'], "1")
        self.assertNotEqual(response.data['results'][0]['data']['view'], response.data['results'][1]['data']['view'])

        # Create store notfication and list control for stores personel
        create_data['receiver'] = self.store
        self.notif_service._create_notification(**create_data)

        response = self.client.get(url, content_type='application/json', **self.washer_headers)
        self.assertEqual(response.data['count'], 3)

        response = self.client.get(url, content_type='application/json', **self.washer2_headers)
        self.assertEqual(response.data['count'], 0)

        response = self.client.get(url, content_type='application/json', **self.worker_headers)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['data']['view_id'], "1")

        response = self.client.get(url, content_type='application/json', **self.customer_headers)
        self.assertEqual(response.data['count'], 0)

        # Error if get wrong x-profile-type

        self.error_headers = {
            'HTTP_AUTHORIZATION': f'Token {self.worker_token}',
            'HTTP_X_PROFILE_TYPE': f'worker123',
        }

        response = self.client.get(url, content_type='application/json', **self.error_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_send_notification(self):
        self.notif_service.send(instance=self.worker_profile,
                                notif_type=NotificationType.reservation_started,
                                to=self.washer_profile)
        self.assertEqual(self.washer_profile.notifications.count(), 1)
        self.assertEqual(self.washer_profile.notifications.last().notification_type,
                         NotificationType.reservation_started)


        self.notif_service.send(instance=self.worker_profile,
                                notif_type=NotificationType.reservation_canceled,
                                to=self.store)
        self.assertEqual(self.washer_profile.notifications.count(), 2)
        self.assertEqual(self.washer_profile.notifications.first().notification_type,
                         NotificationType.reservation_canceled)
        self.assertEqual(self.worker_profile.notifications.count(), 1)
        self.assertEqual(self.worker_profile.notifications.first().notification_type,
                         NotificationType.reservation_canceled)

        self.notif_service.send(instance=self.worker_profile,
                                notif_type=NotificationType.reservation_started,
                                to=self.washer_profile)
        self.assertEqual(self.washer_profile.notifications.count(), 3)
