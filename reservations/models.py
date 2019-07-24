from django.db import models
from enumfields import EnumField

from base.models import StarterModel
from reservations.enums import ReservationStatus


class Reservation(StarterModel):
    status = EnumField(enum=ReservationStatus, default=ReservationStatus.available, db_index=True)
    period = models.PositiveSmallIntegerField()
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(db_index=True)
    basket = models.OneToOneField('baskets.Basket', null=True, on_delete=models.SET_NULL)
    store = models.ForeignKey('stores.Store', on_delete=models.PROTECT)
    customer_profile = models.ForeignKey('users.CustomerProfile', null=True, default=None,
                                         on_delete=models.SET_NULL)
    total_amount = models.DecimalField(decimal_places=2, max_digits=6, null=True, default=None)
    number = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f'{self.status.label}'

    class Meta:
        unique_together = ('start_datetime', 'store', )
        ordering = ['-start_datetime']

class Comment(StarterModel):
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=255)
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='comment')
    reply = models.CharField(max_length=255, null=True)
