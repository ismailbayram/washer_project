from django.utils.translation import ugettext_lazy as _

from enumfields import Enum


class GroupType(Enum):
    customer = 'customer'
    washer = 'washer'
    worker = 'worker'

    class Labels:
        customer = _('Müşteri')
        washer = _('Yıkamacı')
        worker = _('Yıkama Çalışanı')


class Gender(Enum):
    male = 'male'
    female = 'female'

    class Labels:
        male = _('Male')
        female = _('Female')
