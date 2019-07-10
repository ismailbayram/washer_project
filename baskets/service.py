from baskets.models import Basket
from baskets.enums import BasketStatus


class BasketService:
    def get_or_create_basket(self, customer_profile):
        try:
            basket = Basket.objects.get(customer_profile=customer_profile,
                                        status=BasketStatus.active)
        except Basket.DoesNotExist:
            basket = Basket.objects.create(customer_profile=customer_profile,
                                           status=BasketStatus.active,
                                           car=customer_profile.selected_car)
        return basket
