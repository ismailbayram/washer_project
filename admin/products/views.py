from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from products.models import ProductPrice
from admin.products.serializers import ProductPriceSerializer
from admin.products.filters import ProductPriceFilterSet


class ProductPriceAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductPrice.objects.all().select_related('product',
                                                         'product__store',
                                                         'product__store__address').order_by('created_date')
    serializer_class = ProductPriceSerializer
    permission_classes = (IsAdminUser, )
    filter_class = ProductPriceFilterSet

