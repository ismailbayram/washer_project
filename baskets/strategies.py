from baskets.models import DiscountItem
from reservations.enums import ReservationStatus


class BasePromotionStrategy:
    def __init__(self, name):
        self.name = name

    def check(self, basket):
        raise NotImplementedError()

    def apply(self, basket):
        raise NotImplementedError()


class OneFreeInNineStrategy(BasePromotionStrategy):
    def check(self, basket):
        res_count = basket.customer_profile.reservation_set.filter(status=ReservationStatus.completed).count()
        if res_count != 0 and res_count % 9 == 0:
            return True

    def apply(self, basket):
        checked = self.check(basket)
        if checked:
            qs = basket.basketitem_set.filter(product__is_primary=True)
            if qs.exists():
                product = qs.first().product
                discount_item = DiscountItem.objects.create(name=self.name, basket=basket,
                                                            amount=product.price(basket.car.car_type))
