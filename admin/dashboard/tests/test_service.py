import datetime
from decimal import Decimal

from django.utils import timezone
from django.test import TestCase
from model_mommy import mommy

from base.test import BaseTestViewMixin
from admin.dashboard.service import DashboardService
from users.service import UserService
from admin.dashboard.enums import GroupTimeType
from stores.models import Store
from users.models import User
from reservations.models import Reservation
from reservations.service import ReservationService
from users.enums import GroupType


class DashboardServiceTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        super().setUp()
        self.service = DashboardService()
        self.reservation_service = ReservationService()
        self.init_users()
        self.address1 = mommy.make('address.Address')
        self.address2 = mommy.make('address.Address')
        self.address3 = mommy.make('address.Address')
        self.address4 = mommy.make('address.Address')
        self.address5 = mommy.make('address.Address')
        self.address6 = mommy.make('address.Address')
        self.store1 = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                 is_approved=False, is_active=False, address=self.address1,
                                 latitude=35, longitude=34, phone_number="+905388197550")
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=False, address=self.address2,
                                 latitude=35, longitude=34)
        self.store3 = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                 is_approved=True, is_active=False, address=self.address3,
                                 latitude=35, longitude=34, phone_number="+905388197550")
        self.store4 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=False, address=self.address4,
                                 latitude=35, longitude=34)
        self.store5 = mommy.make('stores.Store', washer_profile=self.washer_profile,
                                 is_approved=False, is_active=False, address=self.address5,
                                 latitude=35, longitude=34, phone_number="+905388197550")
        self.store6 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=False, address=self.address6,
                                 latitude=35, longitude=34)

    def init_extra_users(self):
        service = UserService()
        self.superuser = mommy.make('users.User', is_staff=True)
        self.superuser_token = service._create_token(self.superuser)

        data = {
            "first_name": "Customer 3",
            "last_name": "CusLast 3",
            "phone_number": "555555",
            "group_type": GroupType.customer
        }
        self.customer3, self.customer3_token = service.get_or_create_user(**data)
        self.customer3_profile = self.customer3.customer_profile

        data = {
            "first_name": "Customer 4",
            "last_name": "CusLast 4",
            "phone_number": "555556",
            "group_type": GroupType.customer
        }
        self.customer4, self.customer4_token = service.get_or_create_user(**data)
        self.customer4_profile = self.customer4.customer_profile

        data = {
            "first_name": "Worker 3",
            "last_name": "WorkLast 3",
            "phone_number": "555557",
            "group_type": GroupType.worker
        }
        self.worker3, self.worker3_token = service.get_or_create_user(**data)
        self.worker3_profile = self.worker3.worker_profile

        data = {
            "first_name": "Worker 4",
            "last_name": "WorkLast 4",
            "phone_number": "555558",
            "group_type": GroupType.worker
        }
        self.worker4, self.worker4_token = service.get_or_create_user(**data)
        self.worker4_profile = self.worker4.worker_profile

        data = {
            "first_name": "Washer 3",
            "last_name": "WashLast",
            "phone_number": "555559",
            "group_type": GroupType.washer
        }
        self.washer3, self.washer3_token = service.get_or_create_user(**data)
        self.washer3_profile = self.washer3.washer_profile

        data = {
            "first_name": "Washer 4",
            "last_name": "WashLast",
            "phone_number": "555560",
            "group_type": GroupType.washer
        }
        self.washer4, self.washer4_token = service.get_or_create_user(**data)
        self.washer4_profile = self.washer4.washer_profile


    def test_get_stores_waiting_approve(self):
        stores = self.service.get_stores_waiting_approve()
        self.assertEqual(stores[0], self.store1)
        self.assertEqual(stores[1], self.store2)
        self.assertNotEqual(stores[2], self.store3)
        self.assertEqual(stores[2], self.store4)
        self.assertEqual(stores[3], self.store5)
        self.assertEqual(stores[4], self.store6)
        self.store1.is_approved = True
        self.store1.save()
        stores = self.service.get_stores_waiting_approve()
        self.assertNotEqual(stores[0], self.store1)
        self.assertEqual(stores[0], self.store2)

    def test_get_next_date(self):
        dt = datetime.datetime(2019, 12, 31)
        next_date = self.service._get_next_date(dt, GroupTimeType.month)
        self.assertEqual(next_date,
                         timezone.make_aware(datetime.datetime(2020, 1, 1),
                                             timezone.get_default_timezone()))
        next_date = self.service._get_next_date(dt, GroupTimeType.day)
        self.assertEqual(next_date, datetime.datetime(2020, 1, 1))
        dt = datetime.datetime(2019, 12, 31, 23, 47)
        next_date = self.service._get_next_date(dt, GroupTimeType.hour)
        self.assertEqual(next_date, datetime.datetime(2020, 1, 1, 0, 47))

    def test_grouping_with_time(self):
        time_strings = {
            GroupTimeType.hour: "%H:%M",
            GroupTimeType.month: "%d-%m-%Y",
            GroupTimeType.day:  "%d-%m-%Y",
        }
        start_date = timezone.now()
        self.init_extra_users()
        self.address7 = mommy.make('address.Address')
        mommy.make('stores.Store', washer_profile=self.washer2_profile,
                   is_approved=False, address=self.address7,
                   latitude=35, longitude=34)
        self.reservation_service._create_reservation(self.store1, start_date, 40)

        end_date = start_date + datetime.timedelta(days=2)
        group_time = GroupTimeType.day
        users = self.service.grouping_with_time(
            function=self.service.get_total_users_on_grups_count,
            queryset=User.objects.all(),
            lookup_field="date_joined",
            start_date=start_date,
            end_date=end_date,
            group_time=group_time
        )
        stores = self.service.grouping_with_time(
            function=self.service.get_total_store_count,
            queryset=Store.objects.all(),
            lookup_field="created_date",
            start_date=start_date,
            end_date=end_date,
            group_time=group_time
        )
        reservations = self.service.grouping_with_time(
            function=self.service.get_total_reservation_and_profit,
            queryset=Reservation.objects.all(),
            lookup_field='end_datetime',
            start_date=start_date,
            end_date=end_date,
            group_time=group_time
        )
        date = start_date
        self.assertEqual(users[date.strftime(time_strings[group_time])]['customer'], 2)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['worker'], 2)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['washer'], 2)
        self.assertEqual(stores[date.strftime(time_strings[group_time])], 1)
        self.assertEqual(reservations[date.strftime(time_strings[group_time])]['total_reservations'], 1)
        date = date + datetime.timedelta(days=1)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['customer'], 0)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['worker'], 0)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['washer'], 0)
        self.assertEqual(stores[date.strftime(time_strings[group_time])], 0)
        self.assertEqual(reservations[date.strftime(time_strings[group_time])]['total_reservations'], 0)

        group_time = GroupTimeType.month
        next_date = self.service._get_next_date(start_date, group_time)
        end_date = self.service._get_next_date(next_date, group_time)
        users = self.service.grouping_with_time(
            function=self.service.get_total_users_on_grups_count,
            queryset=User.objects.all(),
            lookup_field="date_joined",
            start_date=start_date,
            end_date=end_date,
            group_time=group_time
        )
        stores = self.service.grouping_with_time(
            function=self.service.get_total_store_count,
            queryset=Store.objects.all(),
            lookup_field="created_date",
            start_date=start_date,
            end_date=end_date,
            group_time=group_time
        )
        reservations = self.service.grouping_with_time(
            function=self.service.get_total_reservation_and_profit,
            queryset=Reservation.objects.all(),
            lookup_field='end_datetime',
            start_date=start_date,
            end_date=end_date,
            group_time=group_time
        )
        self.assertEqual(users[start_date.strftime(time_strings[group_time])]['customer'], 2)
        self.assertEqual(users[start_date.strftime(time_strings[group_time])]['worker'], 2)
        self.assertEqual(users[start_date.strftime(time_strings[group_time])]['washer'], 2)
        self.assertEqual(stores[start_date.strftime(time_strings[group_time])], 1)
        self.assertEqual(reservations[start_date.strftime(time_strings[group_time])]['total_reservations'], 1)
        self.assertEqual(users[next_date.strftime(time_strings[group_time])]['customer'], 0)
        self.assertEqual(users[next_date.strftime(time_strings[group_time])]['worker'], 0)
        self.assertEqual(users[next_date.strftime(time_strings[group_time])]['washer'], 0)
        self.assertEqual(stores[next_date.strftime(time_strings[group_time])], 0)
        self.assertEqual(reservations[next_date.strftime(time_strings[group_time])]['total_reservations'], 0)

        end_date = start_date + datetime.timedelta(hours=2)
        group_time = GroupTimeType.hour
        users = self.service.grouping_with_time(
            function=self.service.get_total_users_on_grups_count,
            queryset=User.objects.all(),
            lookup_field="date_joined",
            start_date=start_date,
            end_date=end_date,
            group_time=group_time
        )
        stores = self.service.grouping_with_time(
            function=self.service.get_total_store_count,
            queryset=Store.objects.all(),
            lookup_field="created_date",
            start_date=start_date,
            end_date=end_date,
            group_time=group_time
        )
        reservations = self.service.grouping_with_time(
            function=self.service.get_total_reservation_and_profit,
            queryset=Reservation.objects.all(),
            lookup_field='end_datetime',
            start_date=start_date,
            end_date=end_date,
            group_time=group_time
        )
        date = start_date
        self.assertEqual(users[date.strftime(time_strings[group_time])]['customer'], 2)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['worker'], 2)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['washer'], 2)
        self.assertEqual(stores[date.strftime(time_strings[group_time])], 1)
        self.assertEqual(reservations[date.strftime(time_strings[group_time])]['total_reservations'], 1)
        date = date + datetime.timedelta(hours=1)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['customer'], 0)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['worker'], 0)
        self.assertEqual(users[date.strftime(time_strings[group_time])]['washer'], 0)
        self.assertEqual(stores[date.strftime(time_strings[group_time])], 0)
        self.assertEqual(reservations[date.strftime(time_strings[group_time])]['total_reservations'], 0)

    def test_get_total_user_on_groups_count(self):
        users = User.objects.all()
        dict = self.service.get_total_users_on_grups_count(users)
        self.assertEqual(dict['customer'], 2)
        self.assertEqual(dict['worker'], 2)
        self.assertEqual(dict['washer'], 2)
        self.init_extra_users()
        dict = self.service.get_total_users_on_grups_count(users)
        self.assertEqual(dict['customer'], 4)
        self.assertEqual(dict['worker'], 4)
        self.assertEqual(dict['washer'], 4)

    def test_get_total_store_count(self):
        stores = Store.objects.all()
        count = self.service.get_total_store_count(stores)
        self.assertEqual(count, 6)
        self.address7 = mommy.make('address.Address')
        self.store7 = mommy.make('stores.Store', washer_profile=self.washer2_profile,
                                 is_approved=False, address=self.address7,
                                 latitude=35, longitude=34)
        stores = Store.objects.all()
        count = self.service.get_total_store_count(stores)
        self.assertEqual(count, 7)

    def test_get_total_reservation_and_profit(self):
        dt = timezone.now()
        reservation1 = self.reservation_service._create_reservation(self.store1, dt, 40)
        reservation2 = self.reservation_service._create_reservation(self.store2, dt, 40)
        reservation1.net_amount = 100
        reservation1.save()
        reservation2.net_amount = 200
        reservation2.save()
        reservations = Reservation.objects.all()
        endorsement = Decimal(reservation1.net_amount + reservation2.net_amount)
        profit = endorsement * Decimal(0.15)
        dict = self.service.get_total_reservation_and_profit(reservations)
        self.assertEqual(dict['endorsement'], endorsement)
        self.assertEqual(dict['profit'], profit)
        self.assertEqual(dict['total_reservations'], 2)
        reservation3 = self.reservation_service._create_reservation(self.store3, dt, 40)
        reservation3.net_amount = 500
        reservation3.save()
        endorsement += Decimal(reservation3.net_amount)
        profit = endorsement * Decimal(0.15)
        dict = self.service.get_total_reservation_and_profit(reservations)
        self.assertEqual(dict['endorsement'], endorsement)
        self.assertEqual(dict['profit'], profit)
        self.assertEqual(dict['total_reservations'], 3)

