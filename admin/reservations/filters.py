from django_filters import rest_framework as filters

from reservations.models import CancellationReason

class CancellationReservationFilterSet(filters.FilterSet):
    reason = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = CancellationReason
        fields = ('reason', 'is_active', )
