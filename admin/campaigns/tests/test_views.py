import json

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse_lazy

from model_mommy import mommy
from base.test import BaseTestViewMixin
from admin.campaigns.service import CampaignService


class CampaignViewSetTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.service = CampaignService()
        self.init_users()
        self.campaign = mommy.make('baskets.Campaign')

    def test_create_campaign(self):
        data = {
            "name": "Test Campaign",
            "priority": 10,
            "promotion_type": "one_free_in_nine",
            "is_active": True,
        }
        self.campaign.delete()
        url = reverse_lazy('admin_api:router:campaigns-list')
        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['name'], data['name'])
        self.assertEqual(jresponse['promotion_type'], data['promotion_type'])
        self.assertEqual(jresponse['priority'], data['priority'])
        response = self.client.post(url, data=data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_update_campaign(self):
        data = {
            "name": "Test Campaign",
            "priority": 10,
            "promotion_type": "one_free_in_nine",
            "is_active": False,
        }
        url = reverse_lazy('admin_api:router:campaigns-detail', args=[self.campaign.pk])
        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.put(url, data=data, content_type='application/json', **headers)
        self.campaign.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['name'], self.campaign.name)
        self.assertEqual(jresponse['promotion_type'], self.campaign.promotion_type.value)
        self.assertEqual(jresponse['priority'], self.campaign.priority)
        self.assertFalse(self.campaign.is_active)
        self.assertEqual(data['name'], self.campaign.name)
        self.assertEqual(data['promotion_type'], self.campaign.promotion_type.value)
        self.assertEqual(data['priority'], self.campaign.priority)

    def test_retrieve_campaign(self):
        url = reverse_lazy('admin_api:router:campaigns-detail', args=[self.campaign.pk])

        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jresponse = json.loads(response.content)
        self.assertEqual(jresponse['name'], self.campaign.name)
        self.assertEqual(jresponse['promotion_type'], self.campaign.promotion_type.value)
        self.assertEqual(jresponse['priority'], self.campaign.priority)
        self.assertTrue(self.campaign.is_active)

    def test_list_campaigns(self):
        url = reverse_lazy('admin_api:router:campaigns-list')
        headers = {'HTTP_AUTHORIZATION': f'Token {self.superuser_token}'}
        response = self.client.get(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)