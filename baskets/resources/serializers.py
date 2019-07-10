from rest_framework import serializers

from baskets.models import Basket, BasketItem
from cars.resources.serializers import CarSerializer
from products.resources.serializers import ProductSerializer


class BasketItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source='get_price', max_digits=6,
                                     decimal_places=2, read_only=True)
    product = ProductSerializer()

    class Meta:
        model = BasketItem
        fields = ('product', 'price', )


class BasketSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(source='get_total_amount', max_digits=6,
                                            decimal_places=2, read_only=True)
    car = CarSerializer()
    basketitem_set = BasketItemSerializer(many=True)

    class Meta:
        model = Basket
        fields = ('total_amount', 'car', 'basketitem_set', )
