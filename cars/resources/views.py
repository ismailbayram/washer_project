from rest_framework import viewsets

from api import permissions

from users.enums import GroupType
from cars.resources.serializers import CarSerializer
from cars.models import Car

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
        serializer.save(
            customer_profile=self.request.user.customerprofile
        )
