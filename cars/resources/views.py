import rest_framework.exceptions
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, mixins, views
from rest_framework import decorators
from rest_framework.exceptions import NotFound

from api.permissions import HasGroupPermission, IsCustomerOrReadOnlyPermission
from users.enums import GroupType
from cars.resources.serializers import CarSerializer
from cars.models import Car
from cars.service import CarService

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.filter(is_active=True)
    serializer_class = CarSerializer
    permission_classes = (HasGroupPermission, IsCustomerOrReadOnlyPermission, )
    permission_groups = {
        'create': [GroupType.customer],
        'update': [GroupType.customer],
        'list': [GroupType.customer],
        'partial_update': [GroupType.customer],
        'deactivate': [GroupType.customer],
        'activate': [GroupType.customer],
        'retrieve': [GroupType.customer, GroupType.washer],
        'approve': [GroupType.customer],
        'decline': [GroupType.customer],
    }

    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().list(request, *args, **kwargs)
        self.queryset = request.user.customer_profile.cars.filter(is_active=True).order_by("pk")
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

    @decorators.action(detail=True, methods=['GET'])
    def select(self, request, *args, **kwargs):
        car_pk = self.kwargs.get('pk', None)

        car = Car.objects.get(pk=car_pk)
        service = CarService()
        return_car = service.select_car(car, request.user.customer_profile)
        serializer = self.serializer_class(return_car)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
