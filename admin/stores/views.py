from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from stores.resources.views import StoreViewSet
from stores.service import StoreService
from reservations.tasks import create_store_weekly_reservations


class StoreAdminViewSet(StoreViewSet):
    permission_classes = (IsAdminUser, )

    @action(detail=True, methods=['POST'])
    def approve(self, request, *args, **kwargs):
        service = StoreService()
        instance = self.get_object()
        instance = service.approve_store(instance)
        create_store_weekly_reservations.delay(instance.id)  # TODO: test
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def decline(self, request, *args, **kwargs):
        service = StoreService()
        instance = self.get_object()
        service.decline_store(instance)
        return Response({}, status=status.HTTP_200_OK)
