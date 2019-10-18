import datetime

from django.utils import timezone
from django.test import TestCase

from admin.users.serializers import (WasherProfileSerializer, UserSerializer)

from base.test import BaseTestViewMixin


class UserSerializerTest(BaseTestViewMixin, TestCase):
    def setUp(self):
        self.init_users()

    def test_user_profile_serializer(self):
        expected_data = {
            # 'pk': 22920,
            'date_joined': timezone.now(),
            'last_login': timezone.now(),
            'first_name': 'Washer 1',
            'last_name': 'WashLast',
            'phone_number': '555333',
            'is_active': True,
            'is_customer': False,
            'is_washer': True,
            'is_worker': False
        }

        comming_data = UserSerializer(self.washer).data

        dates = ['date_joined', 'last_login']
        for expected_user_key, expected_user_val in expected_data.items():
            if expected_user_key not in dates:
                self.assertEqual(expected_user_val,
                                 comming_data[expected_user_key])
            else:
                comming_time = datetime.datetime.strptime(
                    comming_data[expected_user_key],
                    "%Y-%m-%dT%H:%M:%S.%f%z"
                )
                self.assertAlmostEqual(
                    comming_time, expected_user_val, delta=datetime.timedelta(
                        seconds=5)
                )

    def test_washer_profile_serializer(self):
        expected_data = {
            # 'pk': 6932,
            'user': {
                # 'pk': 22920,
                'date_joined': timezone.now(),
                'last_login': timezone.now(),
                'first_name': 'Washer 1',
                'last_name': 'WashLast',
                'phone_number': '555333',
                'is_active': True,
                'is_customer': False,
                'is_washer': True,
                'is_worker': False
            }
        }

        comming_data = WasherProfileSerializer(self.washer.washer_profile).data

        dates = ['date_joined', 'last_login']
        for expected_user_key, expected_user_val in expected_data['user'].items():
            if expected_user_key not in dates:
                self.assertEqual(expected_user_val,
                                 comming_data['user'][expected_user_key])
            else:
                comming_time = datetime.datetime.strptime(
                    comming_data['user'][expected_user_key],
                    "%Y-%m-%dT%H:%M:%S.%f%z"
                )
                self.assertAlmostEqual(
                    comming_time, expected_user_val, delta=datetime.timedelta(
                        seconds=5)
                )
