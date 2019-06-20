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
