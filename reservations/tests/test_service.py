import datetime
from decimal import Decimal

import pytz
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone
from model_mommy import mommy

from base.test import BaseTestViewMixin
from baskets.exceptions import BasketEmptyException
from baskets.service import BasketService
from cars.enums import CarType
from cars.service import CarService
from notifications.enums import NotificationType
from products.service import ProductService
from reservations.enums import ReservationStatus
from reservations.exceptions import (ReservationAlreadyCommented,
                                     ReservationAlreadyReplyed,
                                     ReservationCanNotCancelledException,
                                     ReservationCompletedException,
                                     ReservationExpiredException,
                                     ReservationHasNoComment,
                                     ReservationIsNotComplated,
                                     ReservationNotAvailableException,
                                     ReservationOccupiedBySomeoneException,
                                     ReservationStartedException)
from reservations.service import CommentService, ReservationService
from stores.exceptions import StoreNotAvailableException


@override_settings(DEFAULT_PRODUCT_PRICE=Decimal('20.00'))
class ReservationServiceTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.timezone = pytz.timezone(settings.TIME_ZONE)
        self.service = ReservationService()
        self.product_service = ProductService()
        self.car_service = CarService()
        self.basket_service = BasketService()
        self.init_users()
        self.store = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                is_approved=True, is_active=True)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=True, is_active=True)
        self.product1 = self.product_service.create_primary_product(self.store)
        self.product2 = self.product_service.create_product(name='Parfume', store=self.store,
                                                            washer_profile=self.store.washer_profile)
        self.product3 = self.product_service.create_primary_product(self.store2)
        self.car = self.car_service.create_car(licence_plate="34FH3773", car_type=CarType.normal,
                                               customer_profile=self.customer_profile)
        self.store.config = {
            "opening_hours": {
                "monday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "tuesday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "wednesday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "thursday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "friday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "saturday": {
                    "start": "09:00",
                    "end": "18:00"
                },
                "sunday": {
                    "start": None,
                    "end": None
                }
            },
            "reservation_hours": {
                "monday": {
                    "start": None,
                    "end": None
                },
                "tuesday": {
                    "start": None,
                    "end": None
                },
                "wednesday": {
                    "start": None,
                    "end": None
                },
                "thursday": {
                    "start": "09:00",
                    "end": "13:00"
                },
                "friday": {
                    "start": "19:15",
                    "end": "20:00"
                },
                "saturday": {
                    "start": "16:00",
                    "end": "19:00"
                },
                "sunday": {
                    "start": None,
                    "end": None
                }
            }
        }
        self.store.save()

    def test_generate_reservation_number(self):
        number = self.service._generate_reservation_number()
        self.assertEqual(len(number), 10)

    def test_create_reservation(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)
        self.assertEqual(reservation.start_datetime, dt)
        self.assertEqual(reservation.period, 40)
        self.assertEqual(reservation.end_datetime,
                         reservation.start_datetime + datetime.timedelta(minutes=40))

    def test_create_day_from_config(self):
        dt = datetime.datetime(2019, 7, 18, 5, 51)  # Thursday
        res_pk_list = self.service.create_day_from_config(self.store, dt, 30)
        self.assertIsInstance(res_pk_list, list)
        self.assertEqual(len(res_pk_list), 8)
        self.assertEqual(self.store.reservation_set.count(), 8)

        dt = datetime.datetime(2019, 7, 21, 5, 51, 0, 0)  # Sunday
        dt2 = datetime.datetime(2019, 7, 21, 5, 51, 23, 59)  # Sunday
        res_pk_list = self.service.create_day_from_config(self.store, dt, 30)
        self.assertIsInstance(res_pk_list, list)
        self.assertEqual(len(res_pk_list), 0)
        dt = self.timezone.localize(dt)
        dt2 = self.timezone.localize(dt2)
        self.assertEqual(self.store.reservation_set.filter(start_datetime__gt=dt,
                                                           end_datetime__lt=dt2).count(), 0)

    def test_create_week_from_config(self):
        res_pk_list = self.service.create_week_from_config(self.store)
        self.assertIsInstance(res_pk_list, set)
        self.assertEqual(len(res_pk_list), 10)
        self.assertEqual(self.store.reservation_set.count(), 10)

    def test_occupy(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)

        with self.assertRaises(ReservationExpiredException):
            self.service.occupy(reservation, self.customer_profile)

        reservation.start_datetime += datetime.timedelta(minutes=40)
        reservation.save()
        reservation = self.service.occupy(reservation, self.customer_profile)
        self.assertEqual(reservation.status, ReservationStatus.occupied)
        self.assertEqual(reservation.customer_profile, self.customer_profile)

        dt = timezone.now() + datetime.timedelta(minutes=40)
        reservation2 = self.service._create_reservation(self.store, dt, 40)
        reservation2 = self.service.occupy(reservation2, self.customer_profile)
        self.assertEqual(reservation2.status, ReservationStatus.occupied)
        self.assertEqual(reservation2.customer_profile, self.customer_profile)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, ReservationStatus.available)
        self.assertIsNone(reservation.customer_profile)

        with self.assertRaises(ReservationOccupiedBySomeoneException):
            self.service.occupy(reservation2, self.customer2_profile)

        self.store.is_approved = False
        self.store.save()

        with self.assertRaises(StoreNotAvailableException):
            self.service.occupy(reservation, self.customer2_profile)

    def test_reserve(self):
        dt = timezone.now() + datetime.timedelta(minutes=40)
        reservation = self.service._create_reservation(self.store, dt, 40)

        with self.assertRaises(ReservationOccupiedBySomeoneException):
            self.service.reserve(reservation, self.customer_profile)

        reservation.status = ReservationStatus.completed
        reservation.save()

        with self.assertRaises(ReservationNotAvailableException):
            self.service.reserve(reservation, self.customer_profile)

        reservation.status = ReservationStatus.available
        reservation.save()
        self.service.occupy(reservation, self.customer_profile)

        with self.assertRaises(BasketEmptyException):
            self.service.reserve(reservation, self.customer_profile)

        basket = self.basket_service.get_or_create_basket(self.customer_profile)
        self.basket_service.add_basket_item(basket, self.product1)
        reservation = self.service.reserve(reservation, self.customer_profile)

        # START notif test
        self.assertEqual(self.store.washer_profile.notifications.count(), 1)
        self.assertEqual(self.store.washer_profile.notifications.last().notification_type,
                         NotificationType.reservation_reserved)
        # END notif test

        self.assertEqual(reservation.status, ReservationStatus.reserved)
        self.assertEqual(reservation.total_amount, Decimal('20.00'))

        dt = timezone.now() + datetime.timedelta(minutes=40)
        reservation2 = self.service._create_reservation(self.store, dt, 40)
        self.service.occupy(reservation2, self.customer_profile)
        basket = self.basket_service.get_or_create_basket(self.customer_profile)
        self.basket_service.add_basket_item(basket, self.product3)
        with self.assertRaises(BasketEmptyException):
            self.service.reserve(reservation2, self.customer_profile)
        basket = self.basket_service.get_or_create_basket(self.customer_profile)
        self.assertTrue(basket.is_empty)

    def test_start(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)

        with self.assertRaises(ReservationNotAvailableException):
            self.service.start(reservation)

        reservation.status = ReservationStatus.reserved
        reservation.save()
        self.service.start(reservation)

        # START notif test
        self.assertEqual(self.store.washer_profile.notifications.count(), 1)
        self.assertEqual(self.store.washer_profile.notifications.last().notification_type,
                         NotificationType.reservation_started)
        # END notif test

        self.assertEqual(reservation.status, ReservationStatus.started)

        with self.assertRaises(ReservationStartedException):
            self.service.start(reservation)

    def test_complete(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)

        with self.assertRaises(ReservationNotAvailableException):
            self.service.complete(reservation)

        reservation.status = ReservationStatus.started
        reservation.save()
        self.service.complete(reservation)

        # START notif test
        self.assertEqual(self.store.washer_profile.notifications.count(), 1)
        self.assertEqual(self.store.washer_profile.notifications.last().notification_type,
                         NotificationType.reservation_completed)
        # END notif test

        self.assertEqual(reservation.status, ReservationStatus.completed)

        with self.assertRaises(ReservationCompletedException):
            self.service.complete(reservation)

    def test_cancel(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)

        with self.assertRaises(ReservationCanNotCancelledException):
            self.service.cancel(reservation)

        reservation.status = ReservationStatus.reserved
        reservation.customer_profile = self.customer_profile
        reservation.save()
        reservation = self.service.cancel(reservation)

        # START notif test
        self.assertEqual(self.store.washer_profile.notifications.count(), 1)
        self.assertEqual(self.store.washer_profile.notifications.last().notification_type,
                         NotificationType.reservation_canceled)
        self.assertEqual(self.customer_profile.notifications.last().notification_type,
                         NotificationType.reservation_canceled)
        # END notif test

        self.assertEqual(reservation.status, ReservationStatus.cancelled)

    def test_disable(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)
        reservation = self.service.disable(reservation)
        self.assertEqual(reservation.status, ReservationStatus.disabled)

        # START notif test
        self.assertEqual(self.store.washer_profile.notifications.count(), 1)
        self.assertEqual(self.store.washer_profile.notifications.last().notification_type,
                         NotificationType.reservation_disabled)
        # END notif test


        with self.assertRaises(ReservationNotAvailableException):
            self.service.disable(reservation)

    def test_expire(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)
        reservation = self.service.expire(reservation)

        # START notif test
        self.assertEqual(self.store.washer_profile.notifications.count(), 1)
        self.assertEqual(self.store.washer_profile.notifications.last().notification_type,
                         NotificationType.reservation_expired)
        # END notif test

        self.assertEqual(reservation.status, ReservationStatus.expired)


class CommentServiceTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.timezone = pytz.timezone(settings.TIME_ZONE)
        self.service = CommentService()
        self.reservation_service = ReservationService()
        self.product_service = ProductService()
        self.car_service = CarService()
        self.basket_service = BasketService()
        self.init_users()

        self.store = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                is_approved=True, is_active=True)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=True, is_active=True)
        self.product1 = self.product_service.create_primary_product(self.store)
        self.product2 = self.product_service.create_product(name='Parfume', store=self.store,
                                                            washer_profile=self.store.washer_profile)
        self.product3 = self.product_service.create_primary_product(self.store2)
        self.car = self.car_service.create_car(licence_plate="34FH3773", car_type=CarType.normal,
                                               customer_profile=self.customer_profile)

        self.reservation_service = ReservationService()

        dt = datetime.datetime(2019, 7, 18, 5, 51)
        dt = self.timezone.localize(dt)
        dt2 = dt + datetime.timedelta(hours=-1)
        dt3 = dt2 + datetime.timedelta(hours=-1)
        self.reservation = self.reservation_service._create_reservation(self.store, dt, 40)
        self.reservation2 = self.reservation_service._create_reservation(self.store, dt2, 40)
        self.reservation3 = self.reservation_service._create_reservation(self.store, dt3, 40)

    def test_comment(self):
        with self.assertRaises(ReservationIsNotComplated):
            self.service.comment(rating=10, comment="naber", reservation=self.reservation)
        self.reservation.status = ReservationStatus.completed
        self.reservation.save()
        self.reservation2.status = ReservationStatus.completed
        self.reservation2.save()
        self.reservation3.status = ReservationStatus.completed
        self.reservation3.save()

        self.service.comment(rating=10, comment="naber", reservation=self.reservation)

        self.assertEqual(self.reservation.comment.comment, 'naber')
        self.assertEqual(self.reservation.comment.rating, 10)
        self.assertEqual(self.reservation.store.rating, 10)

        with self.assertRaises(ReservationAlreadyCommented):
            self.service.comment(rating=10, comment="naber", reservation=self.reservation)


        self.service.comment(rating=5, comment="naber", reservation=self.reservation2)
        self.service.comment(rating=3, comment="naber", reservation=self.reservation3)

        self.assertEqual(self.store.rating, 6)

    def test_reply(self):
        with self.assertRaises(ReservationHasNoComment):
            self.service.reply("kadir", self.reservation)

        self.reservation.status = ReservationStatus.completed
        self.reservation.save()
        self.service.comment(rating=10, comment="naber", reservation=self.reservation)

        self.service.reply(reply='kadir', reservation=self.reservation)
        self.assertEqual(self.reservation.comment.reply, "kadir")

        with self.assertRaises(ReservationAlreadyReplyed):
            self.service.reply("kadir", self.reservation)
