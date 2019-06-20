from uuid import uuid4
from django.contrib.auth.models import Group
from django.db.transaction import atomic
from rest_framework_jwt.settings import api_settings as jwt_settings

from users.models import User
from users.enums import GroupType
from users.exceptions import UserDoesNotExistException, UserGroupTypeInvalidException


class UserService:
    def create_token(self, phone_number):
        """
        :param phone_number: str
        :return: str
        """
        jwt_response_payload_handler = jwt_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = jwt_settings.JWT_ENCODE_HANDLER
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise UserDoesNotExistException
        payload = jwt_response_payload_handler(user)
        # TODO: update last login
        return jwt_encode_handler(payload)

    @atomic
    def create_user(self, phone_number, first_name, last_name,
                    group_type=GroupType.customer):
        """
        :param phone_number: str
        :param group_type: GroupType
        :param first_name: str
        :param last_name: str
        :return: User
        """
        username = uuid4()
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

        return user

    def deactivate_user(self, user):
        user.is_active = False
        user.save()
        return user
