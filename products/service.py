from django.utils.translation import ugettext_lazy as _
from django.db.transaction import atomic
from django.conf import settings

from stores.exceptions import StoreDoesNotBelongToWasherException
from cars.enums import CarType
from products.models import Product, ProductPrice
from products.enums import ProductType
from products.exceptions import (PeriodIsRequiredException,
                                 PrimaryProductsCanNotDeletedException,
                                 ProductPriceCanNotLessThanException)

PRIMARY_PRODUCT = {
    'name': _('In N Out Washing'),
    'price': settings.DEFAULT_PRODUCT_PRICE,
    'period': 45
}


class ProductService:
    def create_primary_product(self, store):
        # TODO: check second primary product period greater than 60
        """
        :param store: Store
        :return: Product
        """
        product = Product.objects.filter(store=store, is_primary=True).first()
        if product:
            return product
        product = self.create_product(name=PRIMARY_PRODUCT['name'], store=store,
                                      washer_profile=store.washer_profile,
                                      is_primary=True, product_type=ProductType.periodic,
                                      period=PRIMARY_PRODUCT['period'])
        return product

    @atomic
    def create_product(self, name, store, washer_profile, period=None,
                       product_type=ProductType.other, description='',
                       is_primary=False):
        """
        :param name: str
        :param store: Store
        :param washer_profile: WasherProfile
        :param period: int
        :param product_type: ProductType
        :param description: str
        :param is_primary: bool
        :return: Product
        """
        if product_type == ProductType.periodic and period is None:
            raise PeriodIsRequiredException
        if not product_type == ProductType.periodic:
            period = None
        if not store.washer_profile == washer_profile:
            raise StoreDoesNotBelongToWasherException(params=(store, washer_profile))

        product = Product.objects.create(name=name, store=store,
                                         washer_profile=washer_profile,
                                         period=period, product_type=product_type,
                                         description=description, is_primary=is_primary)
        self._create_productprice_set(product)
        return product

    def _create_productprice_set(self, product):
        """
        :param product: Product
        :return: None
        """
        for value, label in CarType.choices():
            ProductPrice.objects.create(product=product, car_type=value,
                                        price=settings.DEFAULT_PRODUCT_PRICE)

    def update_product(self, product, name=None, description=None,
                       period=None, **kwargs):
        """
        :param product: Product
        :param name: str
        :param description: str
        :param kwargs: dict
        :return: Product
        """
        update_fields = []
        if name:
            product.name = name
            update_fields.append('name')

        if description:
            product.description = description
            update_fields.append('description')

        if period and product.product_type == ProductType.periodic:
            product.period = period
            update_fields.append('period')

        product.save(update_fields=update_fields)
        return product

    def update_price(self, product_price, price, **kwargs):
        """
        :param product_price: ProductPrice
        :param price: Decimal
        :param kwargs: dict
        :return: ProductPrice
        """
        if price < settings.MINIMUM_PRODUCT_PRICE:
            raise ProductPriceCanNotLessThanException(params=(product_price.currency.label, ))
        product_price.price = price
        product_price.save(update_fields=['price'])
        return product_price

    def delete_product(self, product):
        """
        :param product: Product
        :return: Product
        """
        if product.is_primary:
            raise PrimaryProductsCanNotDeletedException
        product.is_active = False
        product.save()
        return product
