from django.db import models

from enumfields import EnumField

from users.models import CustomerProfile
from cars.enums import CarType

from base.models import StarterModel


class Car(StarterModel):
    licence_plate = models.CharField(max_length=9)
    car_type = EnumField(CarType)
    customer_profile = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE,
                                         related_name='cars')
    is_active = models.BooleanField(default=True)
    is_selected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('licence_plate', 'customer_profile')
