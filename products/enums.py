from enumfields import Enum
from django.utils.translation import ugettext_lazy as _


class Currency(Enum):
    TRY = 'try'
    USD = 'usd'

    class Labels:
        TRY = _('try')
        USD = _('usd')


class ProductType(Enum):
    periodic = 'periodic'
    # indefinite = 'indefinite'
    other = 'other'

    class Labels:
        periodic = _('Periodic')
        # indefinite = _('Indefinite')
        other = _('Other')
