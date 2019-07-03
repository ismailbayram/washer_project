from django.utils.translation import ugettext_lazy as _

from enumfields import Enum


class CarType(Enum):
    normal = 'binek arac'
    suv = 'suv'
    commercial = 'commercial'
    minibus = 'minibus'

    class Labels:
        normal = _('Binek Araç')
        suv = _('Suv')
        commercial = _('Commercial')
        minibus = _('Minibus')
