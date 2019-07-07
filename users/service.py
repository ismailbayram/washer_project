from uuid import uuid4
from django.contrib.auth.models import Group, update_last_login
from django.db.transaction import atomic
from rest_framework_jwt.settings import api_settings as jwt_settings

from users.models import (User, CustomerProfile, WasherProfile,
                          WorkerProfile)
from users.enums import GroupType
from users.exceptions import (UserGroupTypeInvalidException,
                              WorkerDoesNotBelongToWasherException)
from stores.exceptions import StoreDoesNotBelongToWasherException


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
    def get_or_create_user(self, phone_number, first_name='', last_name='',
                           group_type=GroupType.customer):
        """
        :param phone_number: str
        :param group_type: GroupType
        :param first_name: str
        :param last_name: str
        :return: user: User, token: str
        """
        try:
            group_name = GroupType(group_type).value
        except ValueError:
            raise UserGroupTypeInvalidException

        username = str(uuid4())
        try:
            user = User.objects.get(phone_number=phone_number)
            if user.groups.filter(name=group_name).exists():
                token = self._create_token(user)
                return user, token
        except User.DoesNotExist:
            user = User.objects.create(phone_number=phone_number,
                                       first_name=first_name,
                                       last_name=last_name,
                                       username=username)
            user.set_unusable_password()
            user.save()

        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise UserGroupTypeInvalidException

        self._create_profile(user, group)
        token = self._create_token(user)
        return user, token

    def _create_profile(self, user, group):
        """
        :param user: User
        :param group: Group
        :return: Profile, None
        """
        profiles = {
            'customer': CustomerProfile,
            'washer': WasherProfile,
            'worker': WorkerProfile
        }
        user.groups.add(group)
        profile = profiles[group.name].objects.create(user=user)
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


class WorkerProfileService:
    @atomic
    def create_worker(self, washer_profile, store, phone_number, first_name,
                      last_name):
        """
        :param washer_profile: WasherProfile
        :param store: Store
        :param phone_number: str
        :param first_name: str
        :param last_name: str
        :return: WorkerProfile
        """
        # NOTIFICATION
        if not store.washer_profile == washer_profile:
            raise StoreDoesNotBelongToWasherException(params=(store, washer_profile))
        user_service = UserService()
        worker, _ = user_service.get_or_create_user(phone_number, first_name, last_name,
                                                    group_type=GroupType.worker)
        worker_profile = worker.worker_profile
        if (worker_profile.washer_profile and not worker_profile.washer_profile == washer_profile) \
                or worker.washer_profile:
            raise WorkerDoesNotBelongToWasherException

        worker_profile.washer_profile = washer_profile
        worker_profile.store = store
        worker_profile.save()

        return worker_profile

    def fire_worker(self, worker_profile):
        """
        :param worker_profile: WorkerProfile
        :return: WorkerProfile
        """
        worker_profile.store = None
        worker_profile.washer_profile = None
        worker_profile.save()
        # NOTIFICATION
        return worker_profile

    def move_worker(self, worker_profile, store):
        """
        :param worker_profile: WorkerProfile
        :return: WorkerProfile
        """
        if worker_profile.washer_profile and not store.washer_profile == worker_profile.washer_profile:
            raise StoreDoesNotBelongToWasherException(params=(worker_profile, store.washer_profile))
        worker_profile.store = store
        worker_profile.save()
        # NOTIFICATION
        return worker_profile
