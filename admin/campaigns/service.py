from baskets.models import Campaign
from baskets.enums import PromotionType
from admin.campaigns.exceptions import MultipleOneFreeInNineCampaignException


class CampaignService:
    def create_campaign(self, name, promotion_type, priority, is_active):
        """
        :param name: str
        :param promotion_type: PromotionType
        :param priority: int
        :param is_active: boolean
        :return: Campaign
        """
        if Campaign.objects.filter(promotion_type=PromotionType.one_free_in_nine).exists():
            raise MultipleOneFreeInNineCampaignException(params={
                "campaign_type": promotion_type})
        campaign = Campaign.objects.create(name=name, promotion_type=promotion_type,
                                           priority=priority, is_active=is_active)
        return campaign

    def update_campaign(self, campaign, name, priority, is_active,  **kwargs):
        """
        :param campaign: Campaign
        :param name: str
        :param priority: int
        :param kwargs:
        :return: Campaign
        """
        if Campaign.objects.filter(promotion_type=PromotionType.one_free_in_nine)\
                           .exclude(pk=campaign.pk).exists():
            raise MultipleOneFreeInNineCampaignException(params={
                "campaign_type": PromotionType.one_free_in_nine})
        campaign.name = name
        campaign.priority = priority
        campaign.is_active = is_active
        campaign.save()
        return campaign
