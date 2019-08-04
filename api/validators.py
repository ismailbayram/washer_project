import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def is_valid_phone(phone_number: str):
    res = re.match("\+90\d{10}$", phone_number)
    if res and res.group() == phone_number:
        return True

    raise ValidationError(
        _('Please enter a correct phone number.'),
    )
