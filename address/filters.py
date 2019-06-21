import rest_framework_filters as filters


class CityFilterSet(filters.FilterSet):
    country = filters.NumberFilter(name='country__id', lookup_expr='exact')
