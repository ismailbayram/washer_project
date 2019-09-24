from rest_framework import serializers
from api.fields import EnumField

from cars.enums import CarType
from products.models import Product, ProductPrice
from products.enums import ProductType, Currency
from admin.stores.serializers import StoreSimpleSerializer


class ProductSerializer(serializers.ModelSerializer):
    product_type = EnumField(enum=ProductType)
    store = StoreSimpleSerializer()

    class Meta:
        model = Product
        fields = ('pk', 'name', 'description', 'store',
                  'is_primary', 'product_type', 'period')
        extra_kwargs = {
            'is_primary': {'read_only': True}
        }


class ProductPriceSerializer(serializers.ModelSerializer):
    currency = EnumField(enum=Currency, read_only=True)
    car_type = EnumField(enum=CarType, read_only=True)
    product = ProductSerializer()

    class Meta:
        model = ProductPrice
        fields = ('pk', 'price', 'currency', 'car_type', 'product')
