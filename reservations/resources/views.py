from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import HasGroupPermission
from users.enums import GroupType
from reservations.resources.serializers import ReservationSerializer
from reservations.resources.filters import ReservationFilterSet
from reservations.models import Reservation
from reservations.service import ReservationService


class CustomerReservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reservation.objects.select_related('store', 'store__address',
                                                  'store__address__country',
                                                  'store__address__city',
                                                  'store__address__township').all()
    serializer_class = ReservationSerializer
    service = ReservationService()
    permission_classes = (HasGroupPermission, )
    permission_groups = {
        'list': [GroupType.customer],
        'retrieve': [GroupType.customer],
        'occupy': [GroupType.customer],
        'reserve': [GroupType.customer],
    }
    filter_class = ReservationFilterSet

    def list(self, request, *args, **kwargs):
        q = self.queryset.filter(customer_profile=request.user.customer_profile)
        self.queryset = self.filter_queryset(q)
        return super().list(request, *args, **kwargs)

    @action(methods=['POST'], detail=True)
    def occupy(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation = self.service.occupy(reservation, request.user.customer_profile)
        serializer = self.get_serializer(instance=reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def reserve(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation = self.service.reserve(reservation, request.user.customer_profile)
        serializer = self.get_serializer(instance=reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StoreReservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reservation.objects.select_related('store', 'store__address',
                                                  'store__address__country',
                                                  'store__address__city',
                                                  'store__address__township').all()
    serializer_class = ReservationSerializer
    service = ReservationService()
    permission_classes = (HasGroupPermission,)
    permission_groups = {
        'list': [GroupType.washer, GroupType.worker],
        'retrieve': [GroupType.washer, GroupType.worker],
        'start': [GroupType.washer, GroupType.worker],
        'complete': [GroupType.washer, GroupType.worker],
        'disable': [GroupType.washer, GroupType.worker],
        'cancel': [GroupType.washer, GroupType.worker],
    }
    filter_class = ReservationFilterSet

    def get_queryset(self):
        worker = self.request.user.worker_profile
        if worker:
            return self.queryset.filter(store=worker.store)

        washer = self.request.user.washer_profile
        return self.queryset.filter(store__washer_profile=washer)

    @action(methods=["POST"], detail=True)
    def disable(self, request, *args, **kwargs):
        reservation = self.get_object()
        self._check_object_permission(request, reservation)
        self.service.disable(reservation)
        return Response({}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True)
    def cancel(self, request, *args, **kwargs):
        reservation = self.get_object()
        self._check_object_permission(request, reservation)
        self.service.cancel(reservation)
        return Response({}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True)
    def start(self, request, *args, **kwargs):
        reservation = self.get_object()
        self._check_object_permission(request, reservation)
        self.service.start(reservation)
        return Response({}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True)
    def complete(self, request, *args, **kwargs):
        reservation = self.get_object()
        self._check_object_permission(request, reservation)
        self.service.complete(reservation)
        return Response({}, status=status.HTTP_200_OK)

    def _check_object_permission(self, request, reservation):
        washer_profile = request.user.washer_profile
        worker_profile = request.user.worker_profile
        if worker_profile and not worker_profile.store == reservation.store:
            self.permission_denied(request)
        elif washer_profile and not reservation.store.washer_profile == washer_profile:
            self.permission_denied(request)
        return True


class ReservationListView(views.APIView):
    def get(self, request, *args, **kwargs):
        # TODO: elasticsearch
        return Response({}, status=status.HTTP_200_OK)
