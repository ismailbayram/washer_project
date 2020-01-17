import datetime
from model_mommy import mommy
from unittest.mock import patch

from django.utils import timezone
from django.test import TransactionTestCase, override_settings

from base.test import BaseTestViewMixin
from baskets.service import BasketService
from cars.enums import CarType
from cars.service import CarService
from notifications.models import Notification
from notifications.enums import NotificationType
from reservations.tasks import send_reminder_reservation_notification
from reservations.service import ReservationService
from products.service import ProductService


@override_settings(CELERY_ALWAYS_EAGER=True)
class ReservationTaskTestCase(BaseTestViewMixin, TransactionTestCase):
    def setUp(self):
        self.init_users()
        self.store = mommy.make('stores.Store', is_approved=True, phone_number="05555555555",
                                washer_profile=self.washer_profile)
        self.worker_profile.washer_profile = self.washer_profile
        self.worker_profile.store = self.store
        self.worker_profile.save()
        self.product_service = ProductService()
        self.product1 = self.product_service.create_primary_product(self.store)
        self.car_service = CarService()
        self.car = self.car_service.create_car(licence_plate="34FH3773", car_type=CarType.sedan,
                                               customer_profile=self.customer_profile)
        dt = timezone.now() + datetime.timedelta(minutes=30)
        self.res_service = ReservationService()
        self.reservation = self.res_service._create_reservation(self.store, dt, 40)
        dt = dt + datetime.timedelta(minutes=30)
        self.reservation2 = self.res_service._create_reservation(self.store, dt, 40)
        self.basket_service = BasketService()
        self.basket = self.basket_service.get_or_create_basket(self.customer_profile)

    @patch('reservations.tasks.send_reminder_reservation_notification')
    def test_send_reminder_reservation_notification(self, info):
        self.basket_service.add_basket_item(self.basket, self.product1)
        self.res_service.occupy(self.reservation, self.customer_profile)
        self.res_service.reserve(self.reservation, self.customer_profile)
        self.assertEqual(self.washer_profile.notifications.\
                         filter(notification_type=NotificationType.reservation_reminder_s).count(), 1)
        self.assertEqual(self.worker_profile.notifications. \
                         filter(notification_type=NotificationType.reservation_reminder_s).count(), 1)
        self.assertEqual(self.customer_profile.notifications. \
                         filter(notification_type=NotificationType.reservation_reminder_c).count(), 1)

        task = send_reminder_reservation_notification.delay(self.customer_profile.pk,
                                                            self.reservation2.pk)
        result = task.get()
        self.assertEqual(task.status, 'SUCCESS')
        self.assertFalse(result)
