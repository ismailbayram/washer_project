from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from stores.resources.serializers import StoreSerializer
from stores.models import Store
from admin.dashboard.enums import GroupTimeType
from admin.dashboard.service import DashboardService
from admin.dashboard.serializers import GroupTimeSerializer
from users.models import User
from reservations.enums import ReservationStatus
from reservations.models import Reservation


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAdminUser, )
    service = DashboardService()
    # TODO: cache them all!!!

    @action(methods=['GET'], detail=False)
    def stores_waiting_approve(self, request, *args, **kwargs):
        stores = self.service.get_stores_waiting_approve()
        serializer = StoreSerializer(instance=stores, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def total_counts_without_range(self, request, *args, **kwargs):
        data = self.service.get_total_users_on_grups_count(User.objects.all())
        data.update({
            'store': self.service.get_total_store_count(Store.objects.all())
        })
        return Response(data)

    @action(methods=['GET'], detail=False)
    def total_counts(self, request, *args, **kwargs):
        serializer = GroupTimeSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        users = self.service.grouping_with_time(
            function=self.service.get_total_users_on_grups_count,
            queryset=User.objects.all(),
            lookup_field="date_joined",
            **serializer.validated_data,
        )
        stores = self.service.grouping_with_time(
            function=self.service.get_total_store_count,
            queryset=Store.objects.all(),
            lookup_field="created_date",
            **serializer.validated_data,
        )

        return_dict = {}
        for key, val in users.items():
            val['store'] = stores[key]
            return_dict[key] = val

        return Response(return_dict)

    @action(methods=['GET'], detail=False)
    def reservations(self, request, *args, **kwargs):
        serializer = GroupTimeSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        group_time = serializer.validated_data.get("group_time", GroupTimeType.day)

        return_dict = self.service.grouping_with_time(
            function=self.service.get_total_reservation_and_profit,
            queryset=Reservation.objects.filter(status=ReservationStatus.completed),
            lookup_field='end_datetime',
            **serializer.validated_data
        )

        return Response(return_dict)
