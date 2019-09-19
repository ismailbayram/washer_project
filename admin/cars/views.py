from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from admin.cars.serializers import CarSerializer
from cars.models import Car
from admin.cars.filters import CarFilterSet


class CarAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = (IsAdminUser, )
    filter_class = CarFilterSet
