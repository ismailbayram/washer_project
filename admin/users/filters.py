from django_filters import rest_framework as filters
from django.db.models import Q
from users.models import User, WorkerJobLog
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


class WorkerJobLogFilterSet(filters.FilterSet):
    start_date = filters.IsoDateTimeFromToRangeFilter()
    end_date = filters.IsoDateTimeFromToRangeFilter()
    first_name = filters.CharFilter(field_name='worker_profile__user__first_name',
                                    lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='worker_profile__user__last_name',
                                   lookup_expr='icontains')
    store_name = filters.CharFilter(field_name='store__name', lookup_expr='icontains')
    phone_number = filters.CharFilter(field_name='worker_profile__phone_number',
                                      lookup_expr='exact')
    worker_profile = filters.NumberFilter()
    store = filters.NumberFilter()

    class Meta:
        model = WorkerJobLog
        fields = ('worker_profile', 'store', 'start_date', 'end_date',
                  'first_name', 'last_name', 'store_name', 'phone_number')
