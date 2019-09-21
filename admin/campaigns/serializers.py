from rest_framework import serializers
from api.fields import EnumField

from baskets.enums import PromotionType
from baskets.models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    promotion_type = EnumField(enum=PromotionType)

    class Meta:
        model = Campaign
        fields = ('pk', 'name', 'promotion_type', 'priority', 'is_active')
