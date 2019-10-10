from django_filters import rest_framework as filters

from reservations.models import CancellationReason, Reservation
from reservations.enums import ReservationStatus


class CancellationReservationFilterSet(filters.FilterSet):
    reason = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = CancellationReason
        fields = ('reason', 'is_active', )


class ReservationFilterSet(filters.FilterSet):
    status = filters.ChoiceFilter(choices=ReservationStatus.choices())
    number = filters.CharFilter(lookup_expr='icontains')
    start_datetime = filters.IsoDateTimeFromToRangeFilter()
    end_datetime = filters.IsoDateTimeFromToRangeFilter()
    total_amount = filters.RangeFilter()
    net_amount = filters.RangeFilter()
    customer_profile = filters.NumberFilter()
    comment_rating = filters.RangeFilter(field_name='comment__rating')
    comment = filters.CharFilter(field_name='comment__comment', lookup_expr='icontains')
    period = filters.RangeFilter()

    class Meta:
        model = Reservation
        fields = (
            'number', 'comment', 'start_datetime', 'end_datetime',
            'period', 'store', 'status', 'cancellation_reason',
            'total_amount', 'net_amount', 'customer_profile',
            'comment_rating',
        )
