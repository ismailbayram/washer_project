import datetime
from uuid import uuid4

from django.contrib.auth.models import Group, update_last_login
from django.db.transaction import atomic
from django.db.utils import IntegrityError
from django.utils import timezone
from rest_framework_jwt.settings import api_settings as jwt_settings

from notifications.enums import NotificationType
from notifications.service import NotificationService
from stores.exceptions import StoreDoesNotBelongToWasherException
from users.enums import GroupType
from users.exceptions import (SmsCodeExpiredException,
                              SmsCodeIsInvalidException,
                              SmsCodeIsNotCreatedException,
                              ThereIsUserGivenPhone,
                              UserGroupTypeInvalidException,
                              WorkerDoesNotBelongToWasherException,
                              WorkerHasNoStoreException)
from users.models import (CustomerProfile, SmsMessage, User, WasherProfile,
                          WorkerProfile)


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

    def change_user_names(self, user, first_name, last_name):
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=['first_name', 'last_name'])
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


        return worker_profile

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
        worker_profile.store = store
        worker_profile.washer_profile = store.washer_profile
        worker_profile.save()

        notif_service = NotificationService()
        notif_service.send(instance=worker_profile, notif_type=NotificationType.you_are_fired,
                           to=worker_profile)
        notif_service.send(instance=worker_profile, notif_type=NotificationType.you_fired,
                           to=worker_profile.washer_profile)


        return worker_profile


class SmsService:
    SMS_EXPIRE_TIME = 5 * 60 # sn

    def _create_sms_code(self, phone_number):
        # TODO randomize the code
        now = timezone.now()
        randomized_code = '000000'
        sms_obj = SmsMessage.objects.create(
            code=randomized_code,
            expire_datetime=now + datetime.timedelta(seconds=self.SMS_EXPIRE_TIME),
            phone_number=phone_number,
        )
        return sms_obj

    @atomic
    def get_or_create_sms_code(self, phone_number):
        """
        :param user: User
        :return: SmsMessage
        """
        now = timezone.now()

        create_new_obj = False

        try:
            sms_obj = SmsMessage.objects.get(phone_number=phone_number, is_expired=False)
            if now > sms_obj.expire_datetime:
                create_new_obj = True
                sms_obj.is_expired = True
                sms_obj.save(update_fields=['is_expired'])

        except SmsMessage.DoesNotExist:
            create_new_obj = True

        except SmsMessage.MultipleObjectsReturned:
            # There is no normal way to get this exception but if some anormal
            # things will happen, user can not login anyway. So this two lines
            # solve this problem.
            SmsMessage.objects.filter(phone_number=phone_number).update(is_expired=True)
            create_new_obj = True

        if create_new_obj:
            sms_obj = self._create_sms_code(phone_number)

        return sms_obj


    def _verify_controls(self, phone_number, sms_code):
        """
        :param phone_number: String
        :param sms_code: String
        :return: SmsMessage

        check the is SMS is verifable from sms_code and phone_number
        it checks expiration times and code is true or not
        """
        now = timezone.now()

        try:
            sms_obj = SmsMessage.objects.get(phone_number=phone_number, is_expired=False)

        except SmsMessage.DoesNotExist:
            raise SmsCodeIsNotCreatedException

        if now > sms_obj.expire_datetime:
            sms_obj.is_expired = True
            sms_obj.save(update_fields=['is_expired'])
            raise SmsCodeExpiredException

        if sms_obj.code != sms_code:
            raise SmsCodeIsInvalidException

        return sms_obj


    @atomic
    def verify_sms(self, phone_number, sms_code, *args, **kwargs):
        """
        :param user: User
        :param sms_code: String
        """

        sms_obj = self._verify_controls(phone_number, sms_code)

        user_service = UserService()
        user, _ = user_service.get_or_create_user(phone_number=phone_number)

        if user.is_worker and user.washer_profile is None:
            raise WorkerHasNoStoreException

        sms_obj.is_expired = True
        sms_obj.save(update_fields=['is_expired'])

        return sms_obj


    @atomic
    def verify_sms_when_change_phone(self, phone_number, sms_code, user):
        """
        :param user: User
        :param sms_code: String
        """
        sms_obj = self._verify_controls(phone_number, sms_code)

        try:
            user.phone_number = phone_number
            user.save()
        except IntegrityError:
            raise ThereIsUserGivenPhone

        sms_obj.is_expired = True
        sms_obj.save(update_fields=['is_expired'])

        return sms_obj
