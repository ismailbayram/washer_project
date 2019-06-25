from django.db import models
from django.utils.functional import cached_property
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist

from base.models import StarterModel
from users.enums import GroupType


class User(AbstractUser):
    phone_number = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.get_full_name()

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except ObjectDoesNotExist:
            return None

    @property
    def protected_name(self):
        return f'{self.first_name} {self.last_name[0]}.'

    @cached_property
    def is_customer(self):
        return self.groups.filter(name=GroupType.customer.value).exists()

    @cached_property
    def is_washer(self):
        return self.groups.filter(name=GroupType.washer.value).exists()

    @cached_property
    def is_worker(self):
        return self.groups.filter(name=GroupType.worker.value).exists()


class CustomerProfile(StarterModel):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT, related_name='customer_profile')

    def __str__(self):
        return f'{self.user.get_full_name()}'


class WasherProfile(StarterModel):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT, related_name='washer_profile')

    def __str__(self):
        return f'{self.user.get_full_name()}'


class WorkerProfile(StarterModel):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT, related_name='worker_profile')
    store = models.ForeignKey('stores.Store', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.user.get_full_name()}'

