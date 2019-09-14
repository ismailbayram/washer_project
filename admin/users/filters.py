from django_filters import rest_framework as filters
from django.db.models import Q
from users.models import User
from users.enums import GroupType


class UserFilterSet(filters.FilterSet):
    is_customer = filters.BooleanFilter(method='filter_is_customer')
    is_worker = filters.BooleanFilter(method='filter_is_worker')
    is_washer = filters.BooleanFilter(method='filter_is_washer')
    first_name = filters.CharFilter(lookup_expr='icontains')
    last_name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'is_customer', 'is_worker', 'is_washer',
                  'is_staff', 'is_superuser')

    def filter_is_customer(self, qs, name, value):
        if bool(value):
            return qs.filter(groups__name=GroupType.customer.value)
        return qs.filter(~Q(groups__name=GroupType.customer.value))

    def filter_is_worker(self, qs, name, value):
        if bool(value):
            return qs.filter(groups__name=GroupType.worker.value)
        return qs.filter(~Q(groups__name=GroupType.worker.value))

    def filter_is_washer(self, qs, name, value):
        if bool(value):
            return qs.filter(groups__name=GroupType.washer.value)
        return qs.filter(~Q(groups__name=GroupType.washer.value))
