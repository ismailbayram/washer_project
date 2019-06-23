from rest_framework import viewsets
from api.permissions import HasGroupPermission

from address.models import Country, City, Township, Address
from address.resources.serializers import (CountrySerializer,
                                           CitySerializer,
                                           TownshipSerializer,
                                           AddressSerializer)
from address.filters import CityFilterSet, TownshipFilterSet


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.filter(is_active=True).order_by('name')
    serializer_class = CountrySerializer
    permission_classes = (HasGroupPermission, )
    permission_groups = {
        'create': [],
        'update': [],
        'partial_update': [],
        'destroy': []
    }

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        return instance


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.filter(is_active=True).order_by('name')
    serializer_class = CitySerializer
    filter_class = CityFilterSet
    permission_classes = (HasGroupPermission, )
    permission_groups = {
        'create': [],
        'update': [],
        'partial_update': [],
        'destroy': []
    }

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        return instance


class TownshipViewSet(viewsets.ModelViewSet):
    queryset = Township.objects.filter(is_active=True).order_by('name')
    serializer_class = TownshipSerializer
    filter_class = TownshipFilterSet
    permission_classes = (HasGroupPermission, )
    permission_groups = {
        'create': [],
        'update': [],
        'partial_update': [],
        'destroy': []
    }

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        return instance
