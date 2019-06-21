from django.db import models

from enumfields import EnumField

from users.models import CustomerProfile
from cars.enums import CarType


class Car(models.Model):
    licence_plate = models.CharField(max_length=9)
    car_type = EnumField(CarType)
    customer_profile = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE,
                                         related_name='cars')
    is_active = models.BooleanField(default=True)
