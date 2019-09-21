from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser

from baskets.models import Campaign
from admin.campaigns.serializers import CampaignSerializer
from admin.campaigns.service import CampaignService
from admin.campaigns.filters import CampaignFilterSet


class CampaignAdminViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = (IsAdminUser, )
    filter_class = CampaignFilterSet
    service = CampaignService()

    def perform_create(self, serializer):
        serializer.instance = self.service.create_campaign(**serializer.validated_data)

    def perform_update(self, serializer):
        campaign = self.get_object()
        serializer.instance = self.service.update_campaign(campaign, **serializer.validated_data)
