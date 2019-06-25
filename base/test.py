from model_mommy import mommy

from users.service import UserService
from users.enums import GroupType


class BaseTestMixin:
    def init_users(self):
        service = UserService()
        self.superuser = mommy.make('users.User', is_staff=True)
        self.superuser_token = service._create_token(self.superuser)

        data = {
            "first_name": "Customer 1",
            "last_name": "CusLast",
            "phone_number": "555111",
            "group_type": GroupType.customer
        }
        self.customer, self.customer_token = service.create_user(**data)

        data = {
            "first_name": "Worker 1",
            "last_name": "WorkLast",
            "phone_number": "555222",
            "group_type": GroupType.worker
        }
        self.worker, self.worker_token = service.create_user(**data)

        data = {
            "first_name": "Washer 1",
            "last_name": "WashLast",
            "phone_number": "555333",
            "group_type": GroupType.washer
        }
        self.washer, self.washer_token = service.create_user(**data)
