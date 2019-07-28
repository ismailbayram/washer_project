from baskets.models import DiscountItem
from reservations.enums import ReservationStatus


class BasePromotionStrategy:
    def __init__(self, name):
        self.name = name

    def check(self, basket):
        raise NotImplementedError()

    def get_discount_amount(self, basket_item):
        raise NotImplementedError()

    def apply(self, basket):
        raise NotImplementedError()


class OneFreeInNineStrategy(BasePromotionStrategy):
    def check(self, basket):
        # TODO: return campaign messages if campaign is not applicable
        res_count = basket.customer_profile.reservation_set.filter(status=ReservationStatus.completed).count()
        if res_count != 0 and res_count % 9 == 0:
            return True

    def get_discount_amount(self, basket_item):
        product = basket_item.product
        return product.price(basket_item.basket.car.car_type)

    def apply(self, basket):
        checked = self.check(basket)
        if checked:
            qs = basket.basketitem_set.filter(product__is_primary=True)
            basket_item = qs.first()
            if basket_item and basket_item.discount_item:
                return
            DiscountItem.objects.create(name=self.name, basket=basket, basket_item=basket_item,
                                        amount=self.get_discount_amount(basket_item))
