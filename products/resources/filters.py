from django_filters import rest_framework as filters

from products.models import Product


class ProductFilterSet(filters.FilterSet):
    class Meta:
        model = Product
        fields = ('store', 'is_primary', )
