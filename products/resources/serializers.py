from rest_framework import serializers
from api.fields import EnumField

from cars.enums import CarType
from products.models import Product, ProductPrice
from products.enums import ProductType, Currency


class ProductPriceSerializer(serializers.ModelSerializer):
    currency = EnumField(enum=Currency, read_only=True)
    car_type = EnumField(enum=CarType, read_only=True)

    class Meta:
        model = ProductPrice
        fields = ('pk', 'price', 'currency', 'car_type')


class ProductSerializer(serializers.ModelSerializer):
    product_type = EnumField(enum=ProductType)
    productprice_set = ProductPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('pk', 'name', 'description', 'store', 'productprice_set',
                  'is_primary', 'product_type', 'period')
        extra_kwargs = {
            'is_primary': {'read_only': True}
        }
