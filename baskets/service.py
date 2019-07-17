from django.utils.translation import ugettext_lazy as _

from django.db.models import Q, F
from django.db.transaction import atomic

from baskets.models import Basket, BasketItem
from baskets.enums import BasketStatus
from baskets.exceptions import (PrimaryProductsQuantityMustOne,
                                BasketInvalidException,
                                BasketEmptyException)
from cars.exceptions import CustomerHasNoSelectedCarException


class BasketService:
    def get_or_create_basket(self, customer_profile):
        """
        :param customer_profile: CustomerProfile
        :return: Basket
        """
        if not customer_profile.selected_car:
            raise CustomerHasNoSelectedCarException
        try:
            basket = Basket.objects.get(customer_profile=customer_profile,
                                        status=BasketStatus.active,
                                        car=customer_profile.selected_car)
            self._check_basket_items(basket)
        except Basket.DoesNotExist:
            basket = Basket.objects.create(customer_profile=customer_profile,
                                           status=BasketStatus.active,
                                           car=customer_profile.selected_car)
        return basket

    def _check_basket_items(self, basket):
        """
        :param basket: Basket
        :return: bool
        """
        invalid_items = basket.basketitem_set.exclude(product__is_active=True,
                                                      product__store__is_active=True,
                                                      product__store__is_approved=True)
        if invalid_items:
            msg = _('Some services that are invalid have been removed from your basket: ')

            for bi in invalid_items:
                msg += bi.product.name + ', '
                bi.delete()

            basket.warning_messages.append(msg)

        return not invalid_items.exists()

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

        self._check_basket_items(basket)

        return basket_item

    def clean_basket(self, basket):
        """
        :param basket: Basket
        :return: Basket
        """
        basket.basketitem_set.all().delete()

        return basket

    def delete_basket_item(self, basket, product):
        """
        :param basket: Basket
        :param product: Product
        :return: None
        """
        basket.basketitem_set.filter(product=product).delete()
        self._check_basket_items(basket)

    @atomic
    def complete_basket(self, basket):
        """
        :param basket: Basket
        :return: Basket
        """
        is_basket_valid = self._check_basket_items(basket)
        if not is_basket_valid:
            raise BasketInvalidException
        if basket.is_empty:
            raise BasketEmptyException

        for bi in basket.basketitem_set.all():
            bi.amount = bi.get_price()
            bi.save()
        basket.status = BasketStatus.completed
        basket.save()

        return basket
