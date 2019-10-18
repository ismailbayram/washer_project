from django_filters import rest_framework as filters

from stores.models import Store


class StoreAdminFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    country = filters.CharFilter(field_name='address__country__name', lookup_expr='icontains')
    city = filters.CharFilter(field_name='address__city__name', lookup_expr='icontains')
    township = filters.CharFilter(field_name='address__township__name', lookup_expr='icontains')
    postcode = filters.CharFilter(field_name='address__postcode')
    credit_card = filters.BooleanFilter(field_name='payment_options__credit_card')
    cash = filters.BooleanFilter(field_name='payment_options__cash')
    rating = filters.RangeFilter()

    class Meta:
        model = Store
        fields = (
            'name', 'washer_profile', 'city', 'postcode', 'credit_card',
            'cash', 'rating', 'is_approved', 'is_active'
        )
