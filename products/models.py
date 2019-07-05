from enumfields import EnumField
from django.db import models

from base.models import StarterModel
from products.enums import ProductType, Currency


class Product(StarterModel):
    name = models.CharField(max_length=64)
    product_type = EnumField(enum=ProductType)


class ProductPrice(StarterModel):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    price = models.DecimalField()
    currency = EnumField(enum=Currency)
