from enumfields import Enum


class UserType(Enum):
    user = 'user'
    washer = 'washer'
    worker = 'worker'

    class Labels:
        user = 'User'
        washer = 'Washer'
        worker = 'Worker'
