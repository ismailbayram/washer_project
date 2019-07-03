from model_mommy import mommy
from django.test import TestCase
from django.contrib.auth.models import Group

from users.models import CustomerProfile
from users.service import UserService
from users.exceptions import UserGroupTypeInvalidException
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
            self.service.create_user(**data)

        data.update({"group_type": GroupType.customer})
        user, _ = self.service.create_user(**data)

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

        self.service.create_user(**data)

        data.update({"group_type": GroupType.washer})
        user, _ = self.service.create_user(**data)
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
