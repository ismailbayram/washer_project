from rest_framework import viewsets

from reservations.resources.serializers import ReservationSerializer
from reservations.models import Reservation


class ReservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
