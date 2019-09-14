from django.utils.translation import ugettext_lazy as _

from enumfields import Enum


class GroupType(Enum):
    customer = 'customer'
    washer = 'washer'
    worker = 'worker'

    class Labels:
        customer = _('Customer')
        washer = _('Washer')
        worker = _('Worker')


class Gender(Enum):
    male = 'male'
    female = 'female'

    class Labels:
        male = _('Male')
        female = _('Female')
