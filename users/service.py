from uuid import uuid4

from users.models import User
from users.enums import UserType


class UserService(object):
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
