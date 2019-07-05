from django_filters import rest_framework as filters

from address.models import City, Township


class CityFilterSet(filters.FilterSet):
    class Meta:
        model = City
        fields = ('country', )


class TownshipFilterSet(filters.FilterSet):
    class Meta:
        model = Township
        fields = ('city', )
