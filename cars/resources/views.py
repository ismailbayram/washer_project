from rest_framework import viewsets

from api import permissions

from users.enums import GroupType
from cars.resources.serializers import CarSerializer
from cars.models import Car
from cars.service import CarService


class CarView(viewsets.ModelViewSet):
    permission_classes = (permissions.HasGroupPermission,)

    permission_groups = {
        'create':[GroupType.customer],
    }

    serializer_class = CarSerializer
    queryset = Car.objects.filter(is_active=True)

    def get_queryset(self):
        return self.request.user.customer_profile.customer_profile.all()

    def perform_create(self, serializer):
        servis = CarService()
        data = serializer.validated_data
        servis.create_car(**data)
