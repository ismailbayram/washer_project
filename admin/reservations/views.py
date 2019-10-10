from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from admin.reservations.serializers import CancellationReasonSerializer, \
                                           ReservationDetailedSerializer
from admin.reservations.filters import CancellationReservationFilterSet, \
                                       ReservationFilterSet
from reservations.models import CancellationReason, Reservation
from admin.reservations.serializers import ReservationSerializer
from api.views import MultiSerializerViewMixin


class ReservationCancellationAdminViewSet(ModelViewSet):
    queryset = CancellationReason.objects.all()
    serializer_class = CancellationReasonSerializer
    permission_classes = (IsAdminUser, )
    filter_class = CancellationReservationFilterSet

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        return Response({}, status.HTTP_200_OK)


class ReservationAdminViewSet(MultiSerializerViewMixin, ReadOnlyModelViewSet):
    queryset = Reservation.objects.select_related('store', 'comment',
                                                  'cancellation_reason',
                                                  'store__address',
                                                  'store__address__city',
                                                  'store__address__country',
                                                  'store__address__township', ).all()
    permission_classes = (IsAdminUser, )
    serializer_class = ReservationSerializer
    action_serializers = {
        'retrieve': ReservationDetailedSerializer
    }
    filter_class = ReservationFilterSet

