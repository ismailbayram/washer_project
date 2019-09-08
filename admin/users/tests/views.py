import json

from django.test import TestCase
from model_mommy import mommy
from rest_framework import status
from rest_framework.reverse import reverse_lazy


class AuthViewTest(TestCase):
    def setUp(self):
        self.user = mommy.make('users.User')
        self.user.set_password('123456')

    def test_login(self):
        url = reverse_lazy("admin_api:auth")
        data = {
            "username": self.user.username,
            "password": "123456"
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.is_staff = True
        self.user.save()

        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresp = json.loads(response.content)
        self.assertIn('token', jresp)

