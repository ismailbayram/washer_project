import datetime
from model_mommy import mommy
from decimal import Decimal
from django.test import TestCase, override_settings
from django.utils import timezone

from base.test import BaseTestViewMixin
from baskets.service import BasketService
from baskets.exceptions import BasketEmptyException
from cars.enums import CarType
from cars.service import CarService
from products.service import ProductService
from reservations.service import ReservationService
from reservations.enums import ReservationStatus
from reservations.exceptions import (ReservationNotAvailableException,
                                     ReservationCanNotCancelledException,
                                     ReservationCompletedException,
                                     ReservationStartedException,
                                     ReservationExpiredException,
                                     ReservationOccupiedBySomeoneException)
from stores.exceptions import StoreNotAvailableException


@override_settings(DEFAULT_PRODUCT_PRICE=Decimal('20.00'))
class ReservationServiceTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.service = ReservationService()
        self.product_service = ProductService()
        self.car_service = CarService()
        self.basket_service = BasketService()
        self.init_users()
        self.customer_profile = self.customer.customer_profile
        self.customer2_profile = self.customer2.customer_profile
        self.store = mommy.make('stores.Store', washer_profile=self.washer.washer_profile,
                                is_approved=True, is_active=True)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2.washer_profile,
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
        self.service.create_day_from_config(self.store, dt, 30)
        self.assertEqual(self.store.reservation_set.count(), 8)

        dt = datetime.datetime(2019, 7, 21, 5, 51, 0, 0)  # Sunday
        dt2 = datetime.datetime(2019, 7, 21, 5, 51, 23, 59)  # Sunday
        self.service.create_day_from_config(self.store, dt, 30)
        self.assertEqual(self.store.reservation_set.filter(start_datetime__gt=dt,
                                                           end_datetime__lt=dt2).count(), 0)

    def test_create_week_from_config(self):
        self.service.create_week_from_config(self.store)
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
        self.assertEqual(reservation.status, ReservationStatus.reserved)
        self.assertEqual(reservation.total_amount, Decimal('20.00'))

        dt = timezone.now() + datetime.timedelta(minutes=40)
        reservation2 = self.service._create_reservation(self.store, dt, 40)
        self.service.occupy(reservation2, self.customer_profile)
        basket = self.basket_service.get_or_create_basket(self.customer_profile)
        self.basket_service.add_basket_item(basket, self.product3)
        with self.assertRaises(BasketEmptyException):
            self.service.reserve(reservation2, self.customer_profile)


    def test_start(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)

        with self.assertRaises(ReservationNotAvailableException):
            self.service.start(reservation)

        reservation.status = ReservationStatus.reserved
        reservation.save()
        self.service.start(reservation)
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
        self.assertEqual(reservation.status, ReservationStatus.completed)

        with self.assertRaises(ReservationCompletedException):
            self.service.complete(reservation)

    def test_cancel(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)

        with self.assertRaises(ReservationCanNotCancelledException):
            self.service.cancel(reservation)

        reservation.status = ReservationStatus.reserved
        reservation.save()
        reservation = self.service.cancel(reservation)
        self.assertEqual(reservation.status, ReservationStatus.cancelled)

    def test_disable(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)
        reservation = self.service.disable(reservation)
        self.assertEqual(reservation.status, ReservationStatus.disabled)

        with self.assertRaises(ReservationNotAvailableException):
            self.service.disable(reservation)

    def test_expire(self):
        dt = timezone.now()
        reservation = self.service._create_reservation(self.store, dt, 40)
        reservation = self.service.expire(reservation)
        self.assertEqual(reservation.status, ReservationStatus.expired)
