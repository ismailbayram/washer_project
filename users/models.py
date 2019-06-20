from django.db import models
from django.contrib.auth.models import AbstractUser

from users.enums import GroupType


class User(AbstractUser):
    phone_number = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.get_full_name()

    @property
    def protected_name(self):
        return f'{self.first_name} {self.last_name[0]}.'

    @property
    def is_customer(self):
        return self.groups.filter(name=GroupType.customer.value).exists()

    @property
    def is_washer(self):
        return self.groups.filter(name=GroupType.washer.value).exists()

    @property
    def is_worker(self):
        return self.groups.filter(name=GroupType.worker.value).exists()


class CustomerProfile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT)


class WasherProfile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT)


class WorkerProfile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.PROTECT)

