from django_filters import rest_framework as filters

from cars.models import Car


class CarFilterSet(filters.FilterSet):
    licence_plate = filters.CharFilter(lookup_expr='icontains')
    car_type = filters.CharFilter(field_name="car_type", lookup_expr="exact")
    costumer_profile = filters.CharFilter(field_name='customer_profile', lookup_expr='icontains')

    class Meta:
        model = Car
        fields = ('licence_plate', 'car_type', 'is_selected', 'is_active', 'costumer_profile', )
