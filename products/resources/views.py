from rest_framework import viewsets

from api.permissions import HasGroupPermission, IsWasherOrReadOnlyPermission
from users.enums import GroupType
from products.resources.serializers import (ProductSerializer,
                                            ProductPriceSerializer)
from products.resources.filters import ProductFilterSet
from products.models import Product
from products.service import ProductService


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('productprice_set').all()
    serializer_class = ProductSerializer
    permission_classes = (HasGroupPermission, IsWasherOrReadOnlyPermission)
    permission_groups = {
        'create': [GroupType.washer],
        'list': [GroupType.washer],
        'retrieve': [GroupType.washer],
        'update': [GroupType.washer],
        'partial_update': [GroupType.washer],
        'delete': [GroupType.washer],
        'fire': [GroupType.washer],
        'move': [GroupType.washer],
    }
    filter_class = ProductFilterSet
    service = ProductService()
    # TODO: edit prices with detail endpoint enum

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(washer_profile=self.request.user.washer_profile)

    def perform_create(self, serializer):
        data = serializer.validated_data
        data.update({
            "washer_profile": self.request.user.washer_profile
        })
        serializer.instance = self.service.create_product(**data)

    def perform_destroy(self, instance):
        self.service.delete_product(instance)


# TODO: make seperate viewset like StoreViewSet and add mandatory parameter store in product_list
