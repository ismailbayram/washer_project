import rest_framework.exceptions
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from api.permissions import HasGroupPermission

from users.enums import GroupType
from cars.resources.serializers import CarSerializer
from cars.models import Car
from cars.service import CarService


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.filter(is_active=True)
    serializer_class = CarSerializer
    permission_classes = (HasGroupPermission, )
    permission_groups = {
        'create':[GroupType.customer],
        'update': [GroupType.customer],
        'partial_update': [GroupType.customer],
        'destroy': [GroupType.customer],
    }

    def get_object(self):
        queryset = self.filter_queryset(Car.objects.filter(is_active=True))
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.customer_profile.cars.order_by('id')
        else:
            raise rest_framework.exceptions.NotAuthenticated()

    def perform_create(self, serializer):
        servis = CarService()
        data = serializer.validated_data
        return servis.create_car(**data, user=self.request.user)
