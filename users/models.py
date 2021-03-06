from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.functional import cached_property
from enumfields import EnumField

from base.models import StarterModel
from notifications.models import Notification
from users.enums import GroupType, Gender
from stores.models import Store


class User(AbstractUser):
    phone_number = models.CharField(max_length=255, unique=True)
    gender = EnumField(enum=Gender, null=True)

    def __str__(self):
        return self.get_full_name()

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except ObjectDoesNotExist:
            return None

    @property
    def protected_name(self):
        return '{}. {}.'.format(self.first_name[0].capitalize() if len(self.first_name) > 0 else ' ',
                             self.last_name[0].capitalize() if len(self.last_name) > 0 else ' ')

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
    notifications = GenericRelation(Notification, related_query_name="customer_profile")

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
    notifications = GenericRelation(Notification, related_query_name="washer_profile")

    def __str__(self):
        return f'{self.user.get_full_name()}'


class WorkerProfile(StarterModel):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT, related_name='worker_profile')
    store = models.ForeignKey('stores.Store', on_delete=models.SET_NULL, null=True)
    washer_profile = models.ForeignKey(to=WasherProfile, on_delete=models.SET_NULL, null=True)
    notifications = GenericRelation(Notification, related_query_name="worker_profile")

    def __str__(self):
        return f'{self.user.get_full_name()}'


class WorkerJobLog(StarterModel):
    worker_profile = models.ForeignKey(to=WorkerProfile, on_delete=models.PROTECT, related_name='worker_profile')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    store = models.ForeignKey(to=Store, on_delete=models.PROTECT, related_name='store')
