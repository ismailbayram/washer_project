import imghdr
from uuid import uuid4

from django.contrib.postgres.fields import JSONField
from django.db import models

from base.models import StarterModel
from stores.manager import StoreManager


class Store(StarterModel):
    name = models.CharField(max_length=128)
    washer_profile = models.ForeignKey('users.WasherProfile', on_delete=models.PROTECT)
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
    image = models.ImageField()
    objects = StoreManager()

    def __str__(self):
        return f'{self.name}'



def get_file_name(instance, *args, **kwargs):
    ext = instance.image.name.split(".")[-1]
    return "{0}.{1}".format(uuid4().hex, ext)



class StoreImageItem(StarterModel):
    image = models.ImageField(upload_to=get_file_name)
    store = models.ForeignKey(Store, related_name='images', on_delete=models.CASCADE)
    washer_profile = models.ForeignKey('users.WasherProfile', on_delete=models.CASCADE)
