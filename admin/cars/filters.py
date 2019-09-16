from django_filters import rest_framework as filters
from django.db.models import Q

from cars.models import Car
from cars.enums import CarType


class CarFilterSet(filters.FilterSet):
    licence_plate = filters.CharFilter(lookup_expr='icontains')
    is_normal = filters.BooleanFilter(method='filter_is_normal')
    is_suv = filters.BooleanFilter(method='filter_is_suv')
    is_commercial = filters.BooleanFilter(method='filter_is_commercial')
    is_minibus = filters.BooleanFilter(method='filter_is_minibus')

    class Meta:
        model = Car
        fields = ('licence_plate', 'car_type', 'is_selected', 'is_active', )

    def filter_is_normal(self, qs, name, value):
        if bool(value):
            return qs.filter(car_type=CarType.normal.value)
        return qs.filter(~Q(car_type=CarType.normal.value))

    def filter_is_suv(self, qs, name, value):
        if bool(value):
            return qs.filter(car_type=CarType.suv.value)
        return qs.filter(~Q(car_type=CarType.suv.value))

    def filter_is_commercial(self, qs, name, value):
        if bool(value):
            return qs.filter(car_type=CarType.commercial.value)
        return qs.filter(~Q(car_type=CarType.commercial.value))

    def filter_is_minibus(self, qs, name, value):
        if bool(value):
            return qs.filter(car_type=CarType.minibus.value)
        return qs.filter(~Q(car_type=CarType.minibus.value))
