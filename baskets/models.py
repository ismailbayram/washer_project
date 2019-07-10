from decimal import Decimal
from enumfields.fields import EnumField
from django.db import models

from base.models import StarterModel
from baskets.enums import BasketStatus


class Basket(StarterModel):
    customer_profile = models.ForeignKey('users.CustomerProfile', on_delete=models.PROTECT)
    status = EnumField(enum=BasketStatus)
    car = models.ForeignKey('cars.Car', on_delete=models.PROTECT)

    def get_total_amount(self):
        total_amount = Decimal('0.00')
        for bi in self.basketitem_set.all():
            total_amount += bi.get_price()
        return total_amount


class BasketItem(StarterModel):
    basket = models.ForeignKey(to=Basket, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(null=True, default=None, decimal_places=2, max_digits=6)

    def get_price(self):
        if self.basket.status == BasketStatus.active:
            return self.product.price(self.basket.car.car_type)
        return self.amount
