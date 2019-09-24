from django_filters import rest_framework as filters

from products.models import ProductPrice
from cars.enums import CarType


class ProductPriceFilterSet(filters.FilterSet):
    car_type = filters.ChoiceFilter(choices=CarType.choices())
    price = filters.RangeFilter()
    store = filters.NumberFilter(field_name='product__store')
    name = filters.CharFilter(field_name='product__name', lookup_expr='icontains')

    class Meta:
        model = ProductPrice
        fields = ('price', 'car_type', 'store', 'name', )
