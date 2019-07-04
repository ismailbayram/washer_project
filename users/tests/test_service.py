from model_mommy import mommy
from django.test import TestCase
from django.contrib.auth.models import Group

from users.models import CustomerProfile
from users.service import UserService, WorkerProfileService
from users.exceptions import (UserGroupTypeInvalidException,
                              StoreDoesNotBelongToWasherException,
                              WorkerDoesNotBelongToWasherException)
from users.enums import GroupType


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


class WorkerProfileServiceTest(TestCase):
    def setUp(self):
        user_service = UserService()
        self.service = WorkerProfileService()
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

    def test_fire_worker(self):
        worker_profile = self.service.fire_worker(self.worker_profile)
        self.assertIsNone(worker_profile.store)
        self.assertIsNone(worker_profile.washer_profile)

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
