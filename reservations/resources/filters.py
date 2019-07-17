from django_filters import rest_framework as filters

from reservations.models import Reservation


class ReservationFilterSet(filters.FilterSet):
    class Meta:
        model = Reservation
        fields = ('store', 'status')
