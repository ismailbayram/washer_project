from rest_framework import serializers

from api.fields import EnumField
from baskets.models import Basket, BasketItem, DiscountItem
from cars.resources.serializers import CarSerializer
from products.resources.serializers import ProductSerializer
from products.models import Product
from products.enums import Currency


class CreateBasketItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True,
                                                                                 store__is_approved=True,
                                                                                 store__is_active=True))


class DiscountItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountItem
        fields = ('name', 'amount')


class BasketItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source='get_price', max_digits=6,
                                     decimal_places=2, read_only=True)
    product = ProductSerializer()

    class Meta:
        model = BasketItem
        fields = ('product', 'price', 'quantity',)


class BasketSerializer(serializers.ModelSerializer):
    currency = EnumField(enum=Currency)
    total_amount = serializers.DecimalField(source='get_total_amount', max_digits=6,
                                            decimal_places=2, read_only=True)
    total_quantity = serializers.IntegerField(source='get_total_quantity')
    car = CarSerializer()
    basketitem_set = BasketItemSerializer(many=True)
    warning_messages = serializers.ListField()
    discountitem_set = DiscountItemSerializer(many=True)

    class Meta:
        model = Basket
        fields = ('currency', 'total_amount', 'total_quantity', 'car', 'basketitem_set',
                  'discountitem_set', 'warning_messages',)
