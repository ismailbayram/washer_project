import rest_framework.exceptions
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.permissions import HasGroupPermission, CarIsOwnerOrReadOnlyPermission

from users.enums import GroupType
from cars.resources.serializers import CarSerializer
from cars.models import Car
from cars.service import CarService


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.filter(is_active=True)
    serializer_class = CarSerializer
    permission_classes = (HasGroupPermission, CarIsOwnerOrReadOnlyPermission)
    permission_groups = {
        'create':[GroupType.customer],
        'update': [GroupType.customer],
        'partial_update': [GroupType.customer],
        'destroy': [GroupType.customer],
    }

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({}, status.HTTP_401_UNAUTHORIZED)
        if request.user.is_staff:
            return super().list(request, *args, **kwargs)
        self.queryset = request.user.customer_profile.cars.all().order_by("id")
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        service = CarService()
        data = serializer.validated_data
        serializer.instance = service.create_car(**data, user=self.request.user)

    def perform_update(self, serializer, **kwargs):
        service = CarService()
        data = serializer.validated_data
        serializer.instance = service.update_car(
            car=self.get_object(),
            **data
        )

    def perform_destroy(self, instance):
        service = CarService()
        service.disable_car(instance)
