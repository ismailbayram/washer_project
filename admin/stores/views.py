from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from admin.stores.filters import StoreAdminFilterSet
from admin.stores.serializers import (StoreAdminDetailedSerializer,
                                      StoreSimpleSerializer)
from admin.stores.service import AdminStoreService
from api.views import MultiSerializerViewMixin
from reservations.tasks import create_store_weekly_reservations
from stores.models import Store


class StoreAdminViewSet(MultiSerializerViewMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser, )
    filter_class = StoreAdminFilterSet
    queryset = Store.objects.prefetch_stores()
    serializer_class = StoreSimpleSerializer

    action_serializers = {
        'retrieve': StoreAdminDetailedSerializer
    }

    @action(detail=True, methods=['POST'])
    def approve(self, request, *args, **kwargs):
        service = AdminStoreService()
        instance = self.get_object()
        instance = service.approve_store(instance)
        create_store_weekly_reservations.delay(instance.id)  # TODO: test
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def decline(self, request, *args, **kwargs):
        service = AdminStoreService()
        instance = self.get_object()
        service.decline_store(instance)
        return Response({}, status=status.HTTP_200_OK)
