from enumfields import Enum


class UserType(Enum):
    normal = 'normal'
    washer = 'washer'
    worker = 'worker'

    class Labels:
        normal = 'Normal'
        washer = 'Washer'
        worker = 'Worker'
