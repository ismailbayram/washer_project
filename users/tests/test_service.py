import datetime
from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from notifications.enums import NotificationType
from stores.exceptions import StoreDoesNotBelongToWasherException
from users.enums import GroupType, Gender
from users.exceptions import (SmsCodeExpiredException,
                              SmsCodeIsInvalidException,
                              ThereIsUserGivenPhone,
                              UserGroupTypeInvalidException,
                              WorkerDoesNotBelongToWasherException,
                              WorkerHasNoStoreException)
from users.models import CustomerProfile, User
from users.service import SmsService, UserService, WorkerProfileService, WorkerJobLogService


class UserServiceTest(TestCase):
    def setUp(self):
        self.user = mommy.make('users.User', phone_number="555111")
        self.service = UserService()

    def test_create_token(self):
        self.assertIsNone(self.user.last_login)
        token = self.service._create_token(self.user)
        self.assertIsInstance(token, str)
        self.assertIsNotNone(self.user.last_login)

    def test_create_profile(self):
        customer_group = Group.objects.get(name=GroupType.customer.value)

        customer_profile = self.service._create_profile(self.user, customer_group)
        self.assertIsInstance(customer_profile, CustomerProfile)

    def test_create_user(self):
        data = {
            "phone_number": "555222",
            "first_name": "ismail",
            "last_name": "bayram",
            "group_type": "invalid"
        }
        with self.assertRaises(UserGroupTypeInvalidException):
            self.service.get_or_create_user(**data)

        data.update({"group_type": GroupType.customer})
        user, _ = self.service.get_or_create_user(**data)

        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.phone_number, data["phone_number"])
        self.assertEqual(user.protected_name, "ismail b.")
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_washer, False)
        self.assertEqual(user.is_worker, False)
        self.assertEqual(user.is_customer, True)
        self.assertIsNone(user.washer_profile)
        self.assertIsNotNone(user.customer_profile)
        self.assertIsNone(user.worker_profile)

        self.service.get_or_create_user(**data)

        data.update({"group_type": GroupType.washer})
        user, _ = self.service.get_or_create_user(**data)
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.phone_number, data["phone_number"])
        self.assertEqual(user.protected_name, "ismail b.")
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_washer, True)
        self.assertEqual(user.is_worker, False)
        self.assertEqual(user.is_customer, True)
        self.assertIsNotNone(user.washer_profile)
        self.assertIsNotNone(user.customer_profile)
        self.assertIsNone(user.worker_profile)

    def test_deactivate_user(self):
        self.service.deactivate_user(self.user)
        self.assertEqual(self.user.is_active, False)

    def test_activate_user(self):
        self.service.activate_user(self.user)
        self.assertEqual(self.user.is_active, True)

    def test_change_user_names(self):
        data = {
            "phone_number": "555222",
            "first_name": "ismail",
            "last_name": "bayram",
            "group_type": "washer"
        }
        user,_ = self.service.get_or_create_user(**data)

        self.service.update_user_info(
            user=user,
            first_name="kadir",
            last_name="cetin",
            gender="male",
        )
        user.refresh_from_db()
        self.assertEqual(user.first_name, "kadir")
        self.assertEqual(user.last_name, "cetin")
        self.assertEqual(user.gender, Gender.male)
        self.service.update_user_info(
            user=user,
            first_name="kadir 2",
            last_name="cetin 2",
            gender="male",
        )
        user.refresh_from_db()
        self.assertEqual(user.first_name, "kadir 2")
        self.assertEqual(user.last_name, "cetin 2")
        self.assertEqual(user.gender, Gender.male)


class WorkerProfileServiceTest(TestCase):
    def setUp(self):
        user_service = UserService()
        self.service = WorkerProfileService()
        worker_job_log_service = WorkerJobLogService()
        washer, _ = user_service.get_or_create_user("555111", group_type=GroupType.washer)
        self.washer_profile = washer.washer_profile
        washer2, _ = user_service.get_or_create_user("555112", group_type=GroupType.washer)
        self.washer2_profile = washer2.washer_profile
        self.store = mommy.make('stores.Store', washer_profile=self.washer_profile)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer_profile)
        self.store3 = mommy.make('stores.Store', washer_profile=self.washer2_profile)
        worker, _ = user_service.get_or_create_user("555333", group_type=GroupType.worker)
        self.worker_profile = worker.worker_profile
        self.worker_profile.store = self.store
        self.worker_profile.washer_profile = self.washer_profile
        self.worker_profile.save()
        worker_job_log_service.start_job(self.worker_profile, self.store)

    def test_create_worker(self):
        data = {
            "washer_profile": self.washer2_profile,
            "store": self.store2,
            "phone_number": self.worker_profile.user.phone_number,
            "first_name": self.worker_profile.user.first_name,
            "last_name": self.worker_profile.user.last_name,
        }
        with self.assertRaises(StoreDoesNotBelongToWasherException):
            self.service.create_worker(**data)

        data.update({"store": self.store3})
        with self.assertRaises(WorkerDoesNotBelongToWasherException):
            self.service.create_worker(**data)

        self.worker_profile.washer_profile = None
        self.worker_profile.store = None
        self.worker_profile.save()
        worker_profile = self.service.create_worker(**data)
        self.assertEqual(worker_profile.washer_profile, self.washer2_profile)
        self.assertEqual(worker_profile.store, self.store3)

        data.update({
            "phone_number": self.washer_profile.user.phone_number,
            "first_name": self.washer_profile.user.first_name,
            "last_name": self.washer_profile.user.last_name,
        })
        with self.assertRaises(WorkerDoesNotBelongToWasherException):
            self.service.create_worker(**data)

        data = {
            "washer_profile": self.washer2_profile,
            "store": self.store3,
            "phone_number": "555222",
            "first_name": "Ahmet",
            "last_name": "Cetin"
        }
        worker_profile = self.service.create_worker(**data)
        self.assertEqual(worker_profile.washer_profile, self.washer2_profile)
        self.assertEqual(worker_profile.store, self.store3)

        # notif tests
        self.assertEqual(self.washer2_profile.workerprofile_set.count(), 2)
        self.assertEqual(self.washer2_profile.notifications.count(), 2)
        self.assertEqual(self.washer2_profile.notifications.first().data['worker_name'], "Ahmet Cetin")

    def test_fire_worker(self):
        washer_profile = self.worker_profile.washer_profile

        worker_profile = self.service.fire_worker(self.worker_profile)
        self.assertIsNone(worker_profile.store)
        self.assertIsNone(worker_profile.washer_profile)

        # noif tests
        self.assertEqual(worker_profile.notifications.count(), 1)
        self.assertEqual(worker_profile.notifications.first().notification_type,
                         NotificationType.you_are_fired)
        self.assertEqual(worker_profile.notifications.first().data['worker_name'],
                         "{} {}".format(worker_profile.user.first_name,
                                        worker_profile.user.last_name))

        self.assertEqual(washer_profile.notifications.count(), 1)
        self.assertEqual(washer_profile.notifications.first().notification_type,
                         NotificationType.you_fired)



    def test_move_worker(self):
        with self.assertRaises(StoreDoesNotBelongToWasherException):
            self.service.move_worker(self.worker_profile, self.store3)

        worker_profile = self.service.move_worker(self.worker_profile, self.store2)
        self.assertEqual(worker_profile.store, self.store2)

        self.worker_profile.store = None
        self.worker_profile.washer_profile = None
        self.worker_profile.save()

        worker_profile = self.service.move_worker(self.worker_profile, self.store2)
        self.assertEqual(worker_profile.store, self.store2)
        self.assertEqual(worker_profile.washer_profile, self.store2.washer_profile)

        # notif tests
        self.assertEqual(worker_profile.notifications.count(), 2)
        self.assertEqual(self.washer_profile.notifications.count(), 2)


class SmsServiceTest(TestCase):
    def tearDown(self):
        cache.clear()

    def setUp(self):
        self.service = SmsService()
        user_service = UserService()
        self.worker, _ = user_service.get_or_create_user(phone_number="worker",
                                                        group_type=GroupType.worker.value)
        self.customer, _ = user_service.get_or_create_user(phone_number="+905382451180",
                                                           group_type=GroupType.customer.value)
        self.phone_number = "+905423037159"
        self.phone_number2 = "+905382451188"

    def test_create_sms(self):
        self.service._create_sms_code(self.phone_number2)
        cache_key = self.service.get_cache_key(self.phone_number2)
        sms_code = cache.get(cache_key)

        self.assertIsNotNone(sms_code)

    def test_create_and_verify_sms(self):
        phone_number = '+905555555555'
        with self.assertRaises(SmsCodeExpiredException):
            self.service.verify_sms(phone_number, "tmpcode")

        sms_code = self.service.get_or_create_sms_code(phone_number)
        with self.assertRaises(SmsCodeIsInvalidException):
            self.service.verify_sms(phone_number, '{}{}'.format(sms_code, "wrong"))

        sms_code = self.service.get_or_create_sms_code(self.worker.phone_number)

        with self.assertRaises(WorkerHasNoStoreException):
            self.service.verify_sms(self.worker.phone_number, sms_code)

    def test_verify_sms_when_change_phone(self):
        phone_number = "+901111111111"
        user = User.objects.first()
        self.service.get_or_create_sms_code(phone_number)
        self.service.verify_sms_when_change_phone(phone_number, "000000", user)
        self.assertEqual(user.phone_number, phone_number)

    def test_verify_controls(self):
        with self.assertRaises(SmsCodeExpiredException):
            phone2 = "+905382451187"
            self.service._verify_controls(phone_number=phone2, sms_code="1234")

        phone3 = "+905382451181"

        sms_code = self.service.get_or_create_sms_code(phone3)
        with self.assertRaises(SmsCodeIsInvalidException):
            self.service._verify_controls(
                phone_number=phone3,
                sms_code='{}{}'.format(sms_code, 'invalid')
            )

        self.service._verify_controls(
                phone_number=phone3,
                sms_code=sms_code,
            )


class WorkerJobLogServiceTest(TestCase):
    def setUp(self):
        self.service = WorkerJobLogService()
        user_service = UserService()
        worker, _ = user_service.get_or_create_user(phone_number="+901111111111",
                                                    group_type=GroupType.worker)
        washer, _ = user_service.get_or_create_user(phone_number="+901111111112",
                                                    group_type=GroupType.washer)
        self.washer_profile = washer.washer_profile
        self.store = mommy.make('stores.Store', washer_profile=self.washer_profile)
        self.worker_profile = worker.worker_profile
        self.worker_profile.store = self.store
        self.worker_profile.washer_profile = self.washer_profile
        self.worker_profile.save()

    def test_start_job(self):
        worker_job_log = self.service.start_job(worker_profile=self.worker_profile,
                                                store= self.store)
        d1 = timezone.now()
        d2 = worker_job_log.start_date
        self.assertTrue(abs(d1 - d2) < datetime.timedelta(seconds=1))
        self.assertEqual(worker_job_log.worker_profile, self.worker_profile)
        self.assertEqual(worker_job_log.store, self.store)
        self.assertEqual(worker_job_log.end_date, None)

    def test_end_job(self):
        self.service.start_job(worker_profile=self.worker_profile,
                               store= self.store)
        worker_job_log = self.service.end_job(worker_profile=self.worker_profile)
        d1 = timezone.now()
        d2 = worker_job_log.end_date
        self.assertTrue(abs(d1 - d2) < datetime.timedelta(seconds=1))
        self.assertEqual(worker_job_log.worker_profile, self.worker_profile)
        self.assertEqual(worker_job_log.store, self.store)
