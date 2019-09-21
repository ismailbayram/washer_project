from django.test import TestCase

from base.test import BaseTestViewMixin
from baskets.enums import PromotionType
from baskets.models import Campaign
from admin.campaigns.service import CampaignService
from admin.campaigns.exceptions import MultipleOneFreeInNineCampaignException


class CampaignServiceTest(TestCase, BaseTestViewMixin):
    def setUp(self):
        self.service = CampaignService()

    def test_create_campaign(self):
        data = {
            "name": "Test Campaign",
            "promotion_type": PromotionType.one_free_in_nine,
            "priority": 5,
            "is_active": True
        }
        campaign = self.service.create_campaign(**data)
        self.assertEqual(campaign.name, data['name'])
        self.assertTrue(campaign.is_active)
        self.assertEqual(campaign.promotion_type, data['promotion_type'])
        self.assertEqual(campaign.priority, data['priority'])

        with self.assertRaises(MultipleOneFreeInNineCampaignException):
            self.service.create_campaign(**data)

    def test_update_campaign(self):
        data = {
            "name": "Test Campaign",
            "promotion_type": PromotionType.one_free_in_nine,
            "priority": 5,
        }
        campaign = Campaign.objects.create(**data)
        data.update({
            "name": "Test Campaign Change",
            "priority": 10,
            "is_active": False,

        })
        campaign = self.service.update_campaign(campaign, **data)
        self.assertEqual(campaign.name, data['name'])
        self.assertFalse(campaign.is_active)
        self.assertEqual(campaign.priority, data['priority'])
