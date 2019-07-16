from django.utils.translation import ugettext_lazy as _

from enumfields import Enum


class CarType(Enum):
    normal = 'normal'
    suv = 'suv'
    commercial = 'commercial'
    minibus = 'minibus'

    class Labels:
        normal = _('Binek Araç')
        suv = _('Suv')
        commercial = _('Ticari Araç')
        minibus = _('Minibus')
