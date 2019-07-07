from enumfields import EnumField
from django.db import models

from base.models import StarterModel
from products.enums import ProductType, Currency
from cars.enums import CarType


class Product(StarterModel):
    name = models.CharField(max_length=64)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    washer_profile = models.ForeignKey('users.WasherProfile', on_delete=models.CASCADE)
    product_type = EnumField(enum=ProductType)
    description = models.TextField(max_length=512, default='', blank=True)
    period = models.PositiveSmallIntegerField(default=None, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProductPrice(StarterModel):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=6)
    currency = EnumField(enum=Currency, default=Currency.TRY.value)
    car_type = EnumField(enum=CarType)

    class Meta:
        unique_together = ('product', 'car_type')

    def __str__(self):
        return f'{self.product.name} - {self.price} {self.currency}'
