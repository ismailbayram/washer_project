from uuid import uuid4
from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework_jwt.settings import api_settings as jwt_settings

from users.models import (User, CustomerProfile, WasherProfile,
                          WorkerProfile)
from users.enums import GroupType
from users.exceptions import UserDoesNotExistException, UserGroupTypeInvalidException


class UserService:
    def _create_token(self, user):
        """
        :param user: User
        :return: str
        """
        jwt_response_payload_handler = jwt_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = jwt_settings.JWT_ENCODE_HANDLER
        payload = jwt_response_payload_handler(user)
        # TODO: update last login
        return jwt_encode_handler(payload)

    @transaction.atomic
    def create_user(self, phone_number, first_name, last_name,
                    group_type=GroupType.customer):
        """
        :param phone_number: str
        :param group_type: GroupType
        :param first_name: str
        :param last_name: str
        :return: User
        """
        username = str(uuid4())
        user = User.objects.create(phone_number=phone_number,
                                   first_name=first_name,
                                   last_name=last_name,
                                   username=username)
        user.set_unusable_password()
        try:
            group = Group.objects.get(name=group_type.value)
        except Group.DoesNotExist:
            raise UserGroupTypeInvalidException
        user.groups.add(group)
        self._crete_profile(user, group)
        token = self._create_token(user)
        return user, token

    def _crete_profile(self, user, group):
        if group.name == GroupType.customer.value:
            profile = CustomerProfile.objects.create(user=user)
        elif group.name == GroupType.washer.value:
            profile = WasherProfile.objects.create(user=user)
        elif group.name == GroupType.worker.value:
            profile = WorkerProfile.objects.create(user=user)
        return profile

    def deactivate_user(self, user):
        user.is_active = False
        user.save()
        return user
