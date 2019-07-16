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
        'occupy': [GroupType.customer],
        'reserve': [GroupType.customer],
        'start': [GroupType.washer, GroupType.worker],
        'complete': [GroupType.washer, GroupType.worker],
        'disable': [GroupType.washer, GroupType.worker],
        'cancel': [GroupType.washer, GroupType.worker],
    }

    @action(methods=['POST'], detail=True)
    def occupy(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation = self.service.occupy(reservation, request.user.customer_profile)
        serializer = self.get_serializer(instance=reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True)
    def disable(self, request, *args, **kwargs):
        reservation = self.get_object()
        self._check_object_permission(request, reservation)
        self.service.disable(reservation)
        return Response({}, status=status.HTTP_200_OK)

    def _check_object_permission(self, request, reservation):
        washer_profile = request.user.washer_profile
        worker_profile = request.user.worker_profile
        if worker_profile and not worker_profile.store == reservation.store:
            self.permission_denied(request)
        elif washer_profile and not reservation.store.washer_profile == washer_profile:
            self.permission_denied(request)
        return True

