import datetime
from model_mommy import mommy
from unittest.mock import patch

from django.utils import timezone
from django.test import TestCase, override_settings

from base.test import BaseTestViewMixin
from baskets.service import BasketService
from cars.enums import CarType
from cars.service import CarService
from notifications.enums import NotificationType
from reservations.enums import ReservationStatus
from reservations.models import Reservation
from reservations.tasks import (send_reminder_reservation_notification,
                                prevent_occupying_reservation,
                                create_store_weekly_reservations,
                                check_expired_reservations,
                                create_next_week_day)
from reservations.service import ReservationService
from products.service import ProductService


@override_settings(CELERY_ALWAYS_EAGER=True)
class ReservationTaskTestCase(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.init_users()
        self.address = mommy.make('address.Address')
        self.store = mommy.make('stores.Store', is_approved=True, phone_number="05555555555",
                                washer_profile=self.washer_profile, address=self.address,
                                latitude=2.1, longitude=2.1)
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

    def test_prevent_occupying_reservation(self):
        self.basket_service.add_basket_item(self.basket, self.product1)
        self.res_service.occupy(self.reservation, self.customer_profile)
        prevent_occupying_reservation(self.reservation.pk)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, ReservationStatus.available)
        self.assertEqual(self.reservation.customer_profile, None)

    def test_create_store_weekly_reservations(self):
        self.product1.period = 60
        self.product1.save()
        res_q = Reservation.objects.filter(store=self.store)
        res_q.delete()
        self.store.config = {
            'reservation_hours': {
                'friday': {'end': '19:0', 'start': '16:0'},
                'monday': {'end': '17:0', 'start': '13:0'},
                'sunday': {'end': None, 'start': None},
                'tuesday': {'end': '18:0', 'start': '14:0'},
                'saturday': {'end': '19:0', 'start': '15:0'},
                'thursday': {'end': '17:0', 'start': '15:0'},
                'wednesday': {'end': '19:0', 'start': '14:0'}
            }
        }
        self.store.save()
        create_store_weekly_reservations(self.store.pk)
        self.assertEqual(res_q.count(), 22)

        thursday_reservations = []
        sunday_reservations = []
        for res in res_q:
            if res.start_datetime.weekday() == 3:  # thursday is 3
                thursday_reservations.append(res.pk)
            if res.start_datetime.weekday() == 6:  # sunday is 0
                thursday_reservations.append(res.pk)
        self.assertEqual(len(thursday_reservations), 2)
        self.assertEqual(len(sunday_reservations), 0)

        self.product1.period = 30
        self.product1.save()
        res_q.delete()
        create_store_weekly_reservations(self.store.pk)
        self.assertEqual(res_q.count(), 44)

        thursday_reservations = []
        sunday_reservations = []
        for res in res_q:
            if res.start_datetime.weekday() == 3:  # thursday is 3
                thursday_reservations.append(res.pk)
            if res.start_datetime.weekday() == 6:  # sunday is 0
                thursday_reservations.append(res.pk)
        self.assertEqual(len(thursday_reservations), 4)
        self.assertEqual(len(sunday_reservations), 0)
        self.assertEqual(self.washer_profile.notifications.
                         filter(notification_type=NotificationType.weekly_reservations_created).count(), 2)

    def test_check_expired_reservations(self):
        res_q = Reservation.objects.filter(store=self.store)
        res_q.delete()
        dt = timezone.now()
        dt = dt - datetime.timedelta(days=1)
        self.res_service._create_reservation(self.store, dt, 30)
        dt = dt + datetime.timedelta(minutes=30)
        self.res_service._create_reservation(self.store, dt, 30)
        dt = dt + datetime.timedelta(minutes=30)
        self.res_service._create_reservation(self.store, dt, 30)
        dt = dt + datetime.timedelta(minutes=30)
        self.res_service._create_reservation(self.store, dt, 30)
        self.assertEqual(res_q.filter(status=ReservationStatus.available).count(), 4)

        check_expired_reservations()
        self.assertEqual(res_q.filter(status=ReservationStatus.available).count(), 0)
        self.assertEqual(res_q.filter(status=ReservationStatus.expired).count(), 4)

    def test_create_next_week_day(self):
        res_q = Reservation.objects.filter(store=self.store)
        res_q.delete()

        self.product1.period = 30
        self.product1.save()

        self.store.config = {
            'reservation_hours': {
                'friday': {'end': '13:00', 'start': '12:00'},
                'monday': {'end': '13:00', 'start': '12:00'},
                'sunday': {'end': '13:00', 'start': '12:00'},
                'tuesday': {'end': '13:00', 'start': '12:00'},
                'saturday': {'end': '13:00', 'start': '12:00'},
                'thursday': {'end': '13:00', 'start': '12:00'},
                'wednesday': {'end': '13:00', 'start': '12:00'}
            }
        }
        self.store.save()
        self.assertEqual(res_q.count(), 0)
        create_next_week_day()
        self.assertEqual(res_q.count(), 2)

        dt = (timezone.now() + datetime.timedelta(days=7)).replace(hour=0, minute=0, second=0)
        self.assertEqual(res_q.filter(start_datetime__gte=dt).count(), 2)

