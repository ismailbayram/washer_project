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
        # TODO: check IndexError
        return f'{self.first_name} {self.last_name[0]}.'

    @cached_property
    def user_groups(self):
        return self.groups.all().values_list('name', flat=True)

    @property
    def is_customer(self):
        return GroupType.customer.value in self.user_groups

    @property
    def is_washer(self):
        return GroupType.washer.value in self.user_groups

    @property
    def is_worker(self):
        return GroupType.worker.value in self.user_groups


class CustomerProfile(StarterModel):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT, related_name='customer_profile')

    def __str__(self):
        return f'{self.user.get_full_name()}'

    @property
    def selected_car(self):
        q = self.cars.filter(is_selected=True).first()
        if q:
            return q
        return None


class WasherProfile(StarterModel):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT, related_name='washer_profile')

    def __str__(self):
        return f'{self.user.get_full_name()}'


class WorkerProfile(StarterModel):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT, related_name='worker_profile')
    store = models.ForeignKey('stores.Store', on_delete=models.SET_NULL, null=True)
    washer_profile = models.ForeignKey(to=WasherProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.user.get_full_name()}'

# TODO: add SmsMessageModel: [user, is_expired, expire_datetime, code]
