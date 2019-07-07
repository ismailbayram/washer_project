from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.permissions import HasGroupPermission, IsWasherOrReadOnlyPermission
from users.enums import GroupType
from products.resources.serializers import (ProductSerializer,
                                            ProductPriceSerializer)
from products.resources.filters import ProductFilterSet
from products.models import Product, ProductPrice
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
        'destroy': [GroupType.washer],
        'price': [GroupType.washer],
    }
    filter_class = ProductFilterSet
    service = ProductService()

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

    def perform_update(self, serializer):
        product = self.get_object()
        data = serializer.validated_data
        serializer.instance = self.service.update_product(product, **data)

    def perform_destroy(self, instance):
        self.service.delete_product(instance)

    @action(detail=True, methods=['PUT'], url_path='price/(?P<car_type>[a-zA-Z]+)')
    def price(self, request, car_type, *args, **kwargs):
        product = self.get_object()
        product_price = get_object_or_404(ProductPrice, product=product,
                                          car_type=car_type)
        serializer = ProductPriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.service.update_price(product_price, **serializer.validated_data)
        return Response({}, status=status.HTTP_200_OK)

# TODO: make seperate viewset like StoreViewSet and add mandatory parameter store in product_list
