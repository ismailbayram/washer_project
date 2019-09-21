from django_filters import rest_framework as filters

from baskets.models import Campaign


class CampaignFilterSet(filters.FilterSet):
    promotion_type = filters.CharFilter(field_name="promotion_type", lookup_expr="exact")
    name = filters.CharFilter(lookup_expr='icontains')
    # TODO: Enum Filter

    class Meta:
        model = Campaign
        fields = ('name', 'promotion_type', 'priority', 'is_active')
