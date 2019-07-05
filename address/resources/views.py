from rest_framework import viewsets
from api.permissions import HasGroupPermission

from address.models import Country, City, Township
from address.resources.serializers import (CountrySerializer,
                                           CitySerializer,
                                           TownshipSerializer)
from address.resources.filters import CityFilterSet, TownshipFilterSet
from address.service import (CountryService, CityService,
                             TownshipService)


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
        service = CountryService()
        service.deactive_country(instance)


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
        service = CityService()
        service.deactive_city(instance)


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
        service = TownshipService()
        service.deactive_township(instance)
