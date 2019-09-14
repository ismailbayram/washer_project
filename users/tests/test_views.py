import json

from django.test import TestCase
from model_mommy import mommy
from rest_framework import status
from rest_framework.reverse import reverse_lazy

from base.test import BaseTestViewMixin
from users.enums import GroupType
from users.service import SmsService, UserService


class WorkerProfileViewSetTestView(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.user_service = UserService()
        super().setUp()
        self.init_users()
        self.store = mommy.make('stores.Store', washer_profile=self.washer_profile)
        self.store2 = mommy.make('stores.Store', washer_profile=self.washer2_profile)
        self.store3 = mommy.make('stores.Store', washer_profile=self.washer2_profile)
        self.worker_profile.washer_profile = self.washer.washer_profile
        self.worker_profile.store = self.store
        self.worker_profile.save()
        self.worker2_profile.washer_profile = self.washer2.washer_profile
        self.worker2_profile.store = self.store2
        self.worker2_profile.save()
        self.worker3, _ = self.user_service.get_or_create_user(first_name='Ahmet',
                                                               last_name='Cetin',
                                                               phone_number='+905388197551')
        self.worker3_profile = self.worker3.worker_profile

    def test_list(self):
        url = reverse_lazy('api:router:workers-list')

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)
        self.assertEqual(jresponse['results'][0]['pk'], self.worker_profile.pk)

        url_filtered = f'{url}?store={self.store.pk}'
        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url_filtered, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 1)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['count'], 2)

    def test_retrieve(self):
        url = reverse_lazy('api:router:workers-detail', args=[self.worker_profile.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['pk'], self.worker_profile.pk)

    def test_create(self):
        url = reverse_lazy('api:router:workers-list')
        data = {
            "first_name": "Ahmet",
            "last_name": "Cetin",
            "phone_number": "+905388197550",
            "store": self.store.pk
        }

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data.update({
            "first_name": self.worker3.first_name,
            "last_name": self.worker3.last_name,
            "phone_number": self.worker3.phone_number,
        })
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data.update({"store": self.store2.pk})
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_washer_phone_valid_test(self):
        url = reverse_lazy("api:router:workers-list")
        phones = {
            "+905388197550": True,
            "+905388197555": True,
            "+908388197555": True,
            "+903881975009": True,
            "+95388197550": False,
            "+90538819755": False,
            "+953881975500": False,
            "+9O3881975500": False,
        }

        data = {
            "first_name": "Ahmet",
            "last_name": "Cetin",
            "phone_number": "+905388197550",
            "store": self.store.pk
        }
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}

        for phone, expected_response in phones.items():
            data["phone_number"] = phone
            response = self.client.post(url, data=data, content_type='application/json', **headers)
            if expected_response:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            else:
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fire(self):
        url = reverse_lazy('api:router:workers-fire', args=[self.worker_profile.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_move(self):
        url = reverse_lazy('api:router:workers-move', args=[self.worker_profile.pk, self.store.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse_lazy('api:router:workers-move', args=[self.worker_profile.pk, self.store2.pk])
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse_lazy('api:router:workers-move', args=[self.worker2_profile.pk, self.store.pk])
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer2_token}'}
        response = self.client.post(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update(self):
        url = reverse_lazy('api:router:workers-detail', args=[self.worker_profile.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.put(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.put(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.put(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.patch(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.patch(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.patch(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.patch(url, data={}, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy(self):
        url = reverse_lazy('api:router:workers-detail', args=[self.worker_profile.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.delete(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class SmsViewsTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.sms_service = SmsService()
        super().setUp()

    def test_login(self):
        url = reverse_lazy("api:auth")
        phone1 = "+905388197550"
        phone2 = "+905388197551"

        data = {
            "phone_number": phone1,
            "group_type": GroupType.customer.value
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "phone_number": phone1,
            "group_type": GroupType.washer.value
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "group_type": GroupType.washer.value
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "phone_number": phone1,
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_verify(self):
        url = reverse_lazy("api:auth")
        phone1 = "+905388197550"
        phone2 = "+905388197551"

        data = {
            "phone_number": phone1,
            "group_type": GroupType.washer.value
        }
        response = self.client.post(url, data=data, content_type='application/json')


        url = reverse_lazy("api:sms_verify")

        data = {
            "phone_number": phone2,
            "group_type": "customer",
            "sms_code": "şlkajfşljşlkj"
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        data = {
            "phone_number": phone2,
            "group_type": "customer",
            "sms_code": "000000"
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        data = {
            "phone_number": phone1,
            "group_type": "customer",
            "sms_code": "şlkajfşljşlkj"
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        data = {
            "phone_number": phone1,
            "group_type": "customer",
            "sms_code": "000000"
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        def test_login(self):
            url = reverse_lazy("api:auth")
            data = {
                "phone_number": "+905388197550",
                "group_type": GroupType.customer.value
                }
            response = self.client.post(url, data=data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = {
                "phone_number": "+905388197550",
                "group_type": GroupType.washer.value
            }
            response = self.client.post(url, data=data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = {
                "group_type": GroupType.washer.value
            }
            response = self.client.post(url, data=data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            data = {
                "phone_number": "+905388197550",
            }
            response = self.client.post(url, data=data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_phone_serializer(self):
        url = reverse_lazy("api:auth")
        phones = {
            "+905388197550": True,
            "+905388197555": True,
            "+908388197555": True,
            "+903881975009": True,
            "+95388197550": False,
            "+90538819755": False,
            "+953881975500": False,
            "+9O3881975500": False,
        }

        data = {
            "group_type": GroupType.customer.value
        }

        for phone, expected_response in phones.items():
            data["phone_number"] = phone

            response = self.client.post(url, data=data, content_type='application/json')

            if expected_response:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserInfoTests(TestCase, BaseTestViewMixin):
    def setUp(self):
        super().setUp()
        self.init_users()

    def test_get_user_info(self):
        url = reverse_lazy("api:user-info")

        # For customer
        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        expected = {
            "first_name": "Customer 1",
            "last_name": "CusLast",
            "phone_number": "555111",
        }
        for exp_key, exp_val in expected.items():
            self.assertEqual(exp_val, response.data[exp_key])

        # For worker
        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        expected = {
            "first_name": "Worker 1",
            "last_name": "WorkLast",
            "phone_number": "555222",
        }
        for exp_key, exp_val in expected.items():
            self.assertEqual(exp_val, response.data[exp_key])

        # For washer
        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        expected = {
            "first_name": "Washer 1",
            "last_name": "WashLast",
            "phone_number": "555333",
        }
        for exp_key, exp_val in expected.items():
            self.assertEqual(exp_val, response.data[exp_key])


    def test_set_user_name_customer(self):
        url = reverse_lazy("api:user-info")

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        data = {
            "first_name": "kadir",
            "last_name": "cetin",
            "gender": "male",
        }
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(url, content_type='application/json', **headers)
        expected = {
            "first_name": "kadir",
            "last_name": "cetin",
            "phone_number": "555111",
            "gender": "male",
        }
        for exp_key, exp_val in expected.items():
            self.assertEqual(exp_val, response.data[exp_key])


        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        data = {
            "first_name": "k",
            "last_name": "cetin",
        }
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
        data = {
            "first_name": "kad",
            "last_name": "",
        }
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_set_user_name_worker(self):
        url = reverse_lazy("api:user-info")

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        data = {
            "first_name": "kadir",
            "last_name": "cetin",
            "gender": "male",
        }
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(url, content_type='application/json', **headers)
        expected = {
            "first_name": "kadir",
            "last_name": "cetin",
            "phone_number": "555222",
            "gender": "male",
        }
        for exp_key, exp_val in expected.items():
            self.assertEqual(exp_val, response.data[exp_key])


        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        data = {
            "first_name": "k",
            "last_name": "cetin",
        }
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.worker_token}'}
        data = {
            "first_name": "kad",
            "last_name": "",
        }
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_user_name_washer(self):
        url = reverse_lazy("api:user-info")

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        data = {
            "first_name": "kadir",
            "last_name": "cetin",
            "gender": "male",
        }
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(url, content_type='application/json', **headers)
        expected = {
            "first_name": "kadir",
            "last_name": "cetin",
            "phone_number": "555333",
            "gender": "male",
        }
        for exp_key, exp_val in expected.items():
            self.assertEqual(exp_val, response.data[exp_key])


        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        data = {
            "first_name": "k",
            "last_name": "cetin",
        }
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        headers = {'HTTP_AUTHORIZATION': f'Token {self.washer_token}'}
        data = {
            "first_name": "kad",
            "last_name": "",
        }
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class UserChangePhone(TestCase):
    def setUp(self):
        super().setUp()
        service = UserService()
        data = {
            "first_name": "Customer 1",
            "last_name": "CusLast",
            "phone_number": "+905382451184",
            "group_type": GroupType.customer
        }
        self.customer, self.customer_token = service.get_or_create_user(**data)

        data = {
            "first_name": "washer 12",
            "last_name": "washer",
            "phone_number": "+905382451186",
            "group_type": GroupType.washer
        }
        self.washer, self.washer_token = service.get_or_create_user(**data)

        data = {
            "first_name": "Worker",
            "last_name": "Worker",
            "phone_number": "+905382451185",
            "group_type": GroupType.worker
        }
        self.worker, self.worker_token = service.get_or_create_user(**data)

    def test_change_phone(self):
        test_cases = [
            {
                "token": self.customer_token,
                "phone_number": self.customer.phone_number,
                "phone_to": "+905382451188",
            },
            {
                "token": self.washer_token,
                "phone_number": self.washer.phone_number,
                "phone_to": "+905382451189",
            },
            {
                "token": self.worker_token,
                "phone_number": self.worker.phone_number,
                "phone_to": "+905382451187",
            },
        ]

        for test_case in test_cases:
            url = reverse_lazy("api:set-phone-request")
            headers = {'HTTP_AUTHORIZATION': f'Token {self.customer_token}'}
            data = {"phone_number": test_case['phone_number']}

            response = self.client.post(url, data=data, content_type='application/json', **headers)
            self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

            data = {"phone_number": test_case['phone_to']}
            response = self.client.post(url, data=data, content_type='application/json', **headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            url = reverse_lazy("api:set-phone-verify")
            headers = {'HTTP_AUTHORIZATION': f'Token {test_case["token"]}'}
            data = {"phone_number": test_case['phone_to'], "sms_code": "wrong"}
            response = self.client.post(url, data=data, content_type='application/json', **headers)
            self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

            data = {"phone_number": test_case['phone_to'], "sms_code": "000000"}
            response = self.client.post(url, data=data, content_type='application/json', **headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
