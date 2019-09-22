import six
import binascii
import base64
import uuid

from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


class Base64FieldMixin(object):
    # This class get from https://github.com/Hipo/drf-extra-fields/blob/master/drf_extra_fields/fields.py
    @property
    def ALLOWED_TYPES(self):
        raise NotImplementedError

    @property
    def INVALID_FILE_MESSAGE(self):
        raise NotImplementedError

    @property
    def INVALID_TYPE_MESSAGE(self):
        raise NotImplementedError

    EMPTY_VALUES = (None, '', [], (), {})

    def __init__(self, *args, **kwargs):
        self.represent_in_base64 = kwargs.pop('represent_in_base64', False)
        super(Base64FieldMixin, self).__init__(*args, **kwargs)

    def to_internal_value(self, base64_data):
        # Check if this is a base64 string
        if base64_data in self.EMPTY_VALUES:
            if self.allow_empty_file:
                return None
            raise ValidationError(
                _('Invalid type. This is not an base64 string: {}'.format(
                    type(base64_data)))
            )

        if isinstance(base64_data, six.string_types):
            # Strip base64 header.
            if ';base64,' in base64_data:
                header, base64_data = base64_data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(base64_data)
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)
            # Generate file name:
            file_name = self.get_file_name(decoded_file)
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)
            if file_extension not in self.ALLOWED_TYPES:
                raise ValidationError(self.INVALID_TYPE_MESSAGE)
            complete_file_name = file_name + "." + file_extension
            data = ContentFile(decoded_file, name=complete_file_name)
            return super(Base64FieldMixin, self).to_internal_value(data)
        raise ValidationError(_('Invalid type. This is not an base64 string: {}'.format(
            type(base64_data))))

    def get_file_extension(self, filename, decoded_file):
        raise NotImplementedError

    def get_file_name(self, decoded_file):
        return str(uuid.uuid4())

    def to_representation(self, file):
        if self.represent_in_base64:
            # If the underlying ImageField is blank, a ValueError would be
            # raised on `open`. When representing as base64, simply return an
            # empty base64 str rather than let the exception propagate unhandled
            # up into serializers.
            if not file:
                return ''

            try:
                with open(file.path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                raise IOError("Error encoding file")
        else:
            return super(Base64FieldMixin, self).to_representation(file)
