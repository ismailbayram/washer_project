import datetime
from uuid import uuid4
import hashlib

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import Group, update_last_login
from django.db.transaction import atomic
from django.utils import timezone
from rest_framework_jwt.settings import api_settings as jwt_settings

from notifications.enums import NotificationType
from notifications.service import NotificationService
from stores.exceptions import StoreDoesNotBelongToWasherException
from users.enums import GroupType
from users.exceptions import (SmsCodeExpiredException,
                              SmsCodeIsInvalidException,
                              UserGroupTypeInvalidException,
                              WorkerDoesNotBelongToWasherException,
                              WorkerHasNoStoreException)
from users.models import (CustomerProfile, User, WasherProfile, WorkerProfile, WorkerJobLog)


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
                           group_type=GroupType.customer, *args, **kwargs):
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

    def update_user_info(self, user, first_name, last_name, gender):
        """
        :param user: User
        :param first_name: str
        :param last_name: str
        :param gender: Gender
        :return: User
        """
        user.first_name = first_name
        user.last_name = last_name
        user.gender = gender
        user.save(update_fields=['first_name', 'last_name', 'gender'])
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

        notif_service = NotificationService()
        notif_service.send(instance=worker_profile, to=worker_profile.washer_profile,
                           notif_type=NotificationType.you_has_new_worker)

        worker_job_log_service = WorkerJobLogService()
        worker_job_log_service.start_job(worker_profile, store)

        return worker_profile

    @atomic
    def fire_worker(self, worker_profile):
        """
        :param worker_profile: WorkerProfile
        :return: WorkerProfile
        """
        notif_service = NotificationService()
        notif_service.send(instance=worker_profile, notif_type=NotificationType.you_are_fired,
                           to=worker_profile)
        notif_service.send(instance=worker_profile, notif_type=NotificationType.you_fired,
                           to=worker_profile.washer_profile)

        worker_job_log_service = WorkerJobLogService()
        worker_job_log_service.end_job(worker_profile)

        worker_profile.store = None
        worker_profile.washer_profile = None
        worker_profile.save()

        return worker_profile

    def move_worker(self, worker_profile, store):
        """
        :param worker_profile: WorkerProfile
        :return: WorkerProfile
        """
        if worker_profile.washer_profile and not store.washer_profile == worker_profile.washer_profile:
            raise StoreDoesNotBelongToWasherException(params=(worker_profile, store.washer_profile))

        worker_job_log_service = WorkerJobLogService()
        worker_job_log_service.end_job(worker_profile)

        worker_profile.store = store
        worker_profile.washer_profile = store.washer_profile
        worker_profile.save()

        worker_job_log_service.start_job(worker_profile, store)

        notif_service = NotificationService()
        notif_service.send(instance=worker_profile, notif_type=NotificationType.you_are_fired,
                           to=worker_profile)
        notif_service.send(instance=worker_profile, notif_type=NotificationType.you_fired,
                           to=worker_profile.washer_profile)

        return worker_profile


class SmsService:
    SMS_EXPIRE_TIME = 5 * 60  # sn

    @staticmethod
    def get_cache_key(phone_number):
        cache_key = settings.SMS_CODE_CACHE_KEY_FORMAT.format(hashlib.md5(phone_number.encode()).hexdigest())
        return cache_key

    def _create_sms_code(self, phone_number):
        # TODO randomize the code
        randomized_code = '000000'
        cache_key = self.get_cache_key(phone_number)
        cache.set(cache_key, randomized_code, self.SMS_EXPIRE_TIME)
        return randomized_code

    @atomic
    def get_or_create_sms_code(self, phone_number):
        """
        :param phone_number: User
        """
        cache_key = self.get_cache_key(phone_number)
        sms_code = cache.get(cache_key)
        if not sms_code:
            sms_code = self._create_sms_code(phone_number)
        return sms_code

    def _verify_controls(self, phone_number, sms_code):
        """
        :param phone_number: String
        :param sms_code: String
        :return: SmsMessage

        check the is SMS is verifable from sms_code and phone_number
        it checks expiration times and code is true or not
        """
        cache_sms_code = cache.get(self.get_cache_key(phone_number))
        if not cache_sms_code:
            raise SmsCodeExpiredException

        if sms_code != cache_sms_code:
            raise SmsCodeIsInvalidException

    @atomic
    def verify_sms(self, phone_number, sms_code, *args, **kwargs):
        """
        :param phone_number: String
        :param sms_code: String
        """

        self._verify_controls(phone_number, sms_code)

        user_service = UserService()
        user, _ = user_service.get_or_create_user(phone_number=phone_number)

        if user.is_worker and user.washer_profile is None:
            raise WorkerHasNoStoreException

    @atomic
    def verify_sms_when_change_phone(self, phone_number, sms_code, user):
        """
        :param phone_number: String
        :param sms_code: String
        :param user: User
        """
        self._verify_controls(phone_number, sms_code)

        user.phone_number = phone_number
        user.save()


class WorkerJobLogService:
    def start_job(self, worker_profile, store):
        """
        :param worker_profile: WorkerProfile
        :param store: Store
        :return: WorkerJobLog
        """
        now = timezone.now()

        worker_job_log = WorkerJobLog.objects.create(
            worker_profile=worker_profile,
            start_date=now,
            store=store,
        )

        return worker_job_log

    def end_job(self, worker_profile):
        """
        :param worker_profile: WorkerProfile
        :return: WorkerJobLog
        """
        now = timezone.now()

        worker_job_log = WorkerJobLog.objects.filter(worker_profile=worker_profile).order_by('pk').last()
        worker_job_log.end_date = now
        worker_job_log.save()

        return worker_job_log
