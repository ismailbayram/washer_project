from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import HasGroupPermission
from users.enums import GroupType
from reservations.resources.serializers import ReservationSerializer
from reservations.models import Reservation
from reservations.service import ReservationService


class ReservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    service = ReservationService()
    permission_classes = (HasGroupPermission, )
    permission_groups = {
        'occupy': [GroupType.customer]
    }

    @action(methods=['POST'], detail=True)
    def occupy(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation = self.service.occupy(reservation, request.user.customer_profile)
        serializer = self.get_serializer(instance=reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)
