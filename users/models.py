from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (PermissionsMixin, UserManager)

from enumfields import EnumField

from users.enums import UserType


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    date_joined = models.DateTimeField(default=timezone.now)
    phone_number = models.CharField(max_length=255)
    user_type = EnumField(UserType, default=UserType.user, max_length=255)
    username = models.CharField(max_length=255, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        unique_together = ('phone_number', 'user_type')

    def __str__(self):
        return f'{self.full_name} - {self.user_type.value}'

    def get_username(self):
        return self.phone_number

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def protected_name(self):
        return f'{self.first_name} {self.last_name[0]}.'
