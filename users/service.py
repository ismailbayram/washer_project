from uuid import uuid4
from rest_framework_jwt.settings import api_settings as jwt_settings

from users.models import User
from users.enums import UserType
from users.exceptions import UserDoesNotExistException


class UserService(object):
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
        return jwt_encode_handler(payload)

    def create_user(self, phone_number, user_type=UserType.normal,
                    first_name=None, last_name=None):
        """
        :param phone_number: str
        :param user_type: UserType
        :param first_name: str
        :param last_name: str
        :return: User
        """
        username = uuid4()
        user = User.objects.create(phone_number=phone_number,
                                   user_type=user_type,
                                   first_name=first_name,
                                   last_name=last_name,
                                   username=username)
        user.set_unusable_password()

        return user
