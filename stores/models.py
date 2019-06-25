from django.db import models
from django.contrib.postgres.fields import JSONField

from base.models import StarterModel


class Store(StarterModel):
    name = models.CharField(max_length=128)
    washer_profile = models.ForeignKey('users.WasherProfile', on_delete=models.PROTECT, null=True)
    address = models.OneToOneField('address.Address', on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=32)
    tax_office = models.CharField(max_length=128)
    tax_number = models.CharField(max_length=128)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    config = JSONField(default=dict)  # open hours and open reservations
    latitude = models.FloatField(default=None, null=True)
    longitude = models.FloatField(default=None, null=True)
    rating = models.FloatField(default=None, null=True)
    # TODO: add manager for geohash algorithm

    def __str__(self):
        return f'{self.name}'
