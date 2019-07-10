from django.db.models import Q, F
from django.db.transaction import atomic

from baskets.models import Basket, BasketItem
from baskets.enums import BasketStatus
from baskets.exceptions import PrimaryProductsQuantityMustOne


class BasketService:
    def get_or_create_basket(self, customer_profile):
        """
        :param customer_profile: CustomerProfile
        :return: Basket
        """
        try:
            basket = Basket.objects.get(customer_profile=customer_profile,
                                        status=BasketStatus.active,
                                        car=customer_profile.selected_car)
        except Basket.DoesNotExist:
            basket = Basket.objects.create(customer_profile=customer_profile,
                                           status=BasketStatus.active,
                                           car=customer_profile.selected_car)
        return basket

    def add_basket_item(self, basket, product):
        """
        :param basket: Basket
        :param product: Product
        :return: BasketItem
        """
        if not basket.is_empty and basket.basketitem_set.filter(~Q(product__store=product.store)).exists():
            self.clean_basket(basket)

        try:
            basket_item = basket.basketitem_set.get(product=product)
            if basket_item.product.is_primary:
                raise PrimaryProductsQuantityMustOne
            basket_item.quantity = F('quantity') + 1
            basket_item.save()
        except BasketItem.DoesNotExist:
            basket_item = BasketItem.objects.create(basket=basket, product=product)

        return basket_item

    def clean_basket(self, basket):
        """
        :param basket: Basket
        :return: None
        """
        basket.basketitem_set.all().delete()

    @atomic
    def complete_basket(self, basket):
        """
        :param basket: Basket
        :return: Basket
        """
        for bi in basket.basketitem_set.all():
            bi.amount = bi.get_price()
            bi.save()
        basket.status = BasketStatus.completed
        basket.save()

        return basket
