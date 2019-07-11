from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import HasGroupPermission
from users.enums import GroupType
from baskets.service import BasketService
from baskets.resources.serializers import BasketSerializer, CreateBasketItemSerializer


class BasketViewSet(viewsets.ViewSet):
    permission_classes = (HasGroupPermission,)
    permission_groups = {
        'view_basket': [GroupType.customer]
    }
    service = BasketService()

    @action(methods=['GET'], detail=False)
    def view_basket(self, request, *args, **kwargs):
        basket = self.service.get_or_create_basket(request.user.customer_profile)
        serializer = BasketSerializer(instance=basket)
        return Response({'basket': serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def add_item(self, request, *args, **kwargs):
        serializer = CreateBasketItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        basket = self.service.get_or_create_basket(request.user.customer_profile)
        self.service.add_basket_item(basket, **serializer.validated_data)
        serializer = BasketSerializer(instance=basket)
        return Response({'basket': serializer.data}, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE'], detail=False)
    def delete_item(self, request, *args, **kwargs):
        serializer = CreateBasketItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        basket = self.service.get_or_create_basket(request.user.customer_profile)
        self.service.delete_basket_item(basket, **serializer.validated_data)
        serializer = BasketSerializer(instance=basket)
        return Response({'basket': serializer.data}, status=status.HTTP_204_NO_CONTENT)
