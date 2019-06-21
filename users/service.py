from uuid import uuid4
from django.contrib.auth.models import Group, update_last_login
from django.db.transaction import atomic
from django.db import IntegrityError
from rest_framework_jwt.settings import api_settings as jwt_settings

from users.models import (User, CustomerProfile, WasherProfile,
                          WorkerProfile)
from users.enums import GroupType
from users.exceptions import (UserGroupTypeInvalidException,
                              UserAlreadyExistException)


class UserService:
    def _create_token(self, user):
        """
        :param user: User
        :return: str
        """
        jwt_response_payload_handler = jwt_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = jwt_settings.JWT_ENCODE_HANDLER
        payload = jwt_response_payload_handler(user)
        update_last_login(User, user)

        return jwt_encode_handler(payload)

    @atomic
    def create_user(self, phone_number, first_name, last_name,
                    group_type=GroupType.customer):
        """
        :param phone_number: str
        :param group_type: GroupType
        :param first_name: str
        :param last_name: str
        :return: user: User, token: str
        """
        username = str(uuid4())
        try:
            User.objects.get(phone_number=phone_number)
            raise UserAlreadyExistException
        except User.DoesNotExist:
            pass

        user = User.objects.create(phone_number=phone_number,
                                   first_name=first_name,
                                   last_name=last_name,
                                   username=username)
        user.set_unusable_password()

        try:
            group = Group.objects.get(name=group_type.value)
        except Group.DoesNotExist:
            raise UserGroupTypeInvalidException

        self._crete_profile(user, group)
        token = self._create_token(user)
        return user, token

    def _crete_profile(self, user, group):
        """
        :param user: User
        :param group: Group
        :return: Profile, None
        """
        groups = {
            'customer': CustomerProfile,
            'washer': WasherProfile,
            'worker': WorkerProfile
        }
        try:
            user.groups.add(group)
            profile = groups[group.name].objects.create(user=user)
        except KeyError:
            #TODO: log here
            return None
        except IntegrityError:
            return getattr(user, '{}_profile'.format(group.name))
        return profile

    def deactivate_user(self, user):
        """
        :param user: User
        :return: User
        """
        user.is_active = False
        user.save()
        return user

    def activate_user(self, user):
        """
        :param user: User
        :return: User
        """
        user.is_active = True
        user.save()
        return user
