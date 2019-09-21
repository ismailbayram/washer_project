from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from admin.reservations.serializers import CancellationReasonSerializer
from admin.reservations.filters import CancellationReservationFilterSet
from reservations.models import CancellationReason



class ReservationCancellationAdminViewSet(ModelViewSet):
    queryset = CancellationReason.objects.all()
    serializer_class = CancellationReasonSerializer
    permission_classes = (IsAdminUser, )
    filter_class = CancellationReservationFilterSet

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        return Response({}, status.HTTP_200_OK)
