from django.db.transaction import atomic

from stores.exceptions import StoreDoesNotBelongToWasherException
from products.models import Product
from products.enums import ProductType
from products.exceptions import PeriodIsRequiredException


class ProductService:
    def create_product(self, name, store, washer_profile, period=None,
                       product_type=ProductType.other, description=''):
        """
        :param name: str
        :param store: Store
        :param washer_profile: WasherProfile
        :param period: int
        :param product_type: ProductType
        :param description: str
        :return: Product
        """
        if product_type == ProductType.periodic and period is None:
            raise PeriodIsRequiredException
        if not store.washer_profile == washer_profile:
            raise StoreDoesNotBelongToWasherException(params=(store, washer_profile))

        period = None
        product = Product.objects.create(name=name, store=store,
                                         washer_profile=washer_profile,
                                         period=period, product_type=product_type,
                                         description=description)

        return product

    @atomic
    def delete_product(self, product):
        """
        :param product: Product
        :return: bool
        """
        product.productprice_set.all().delete()
        product.delete()
        return True
