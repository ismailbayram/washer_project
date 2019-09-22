import imghdr
import io
import base64

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.fields import ImageField

from .mixins import Base64FieldMixin


class EnumField(serializers.ChoiceField):
    def __init__(self, enum, **kwargs):
        self.enum = enum
        kwargs['choices'] = [(e.name, e.name) for e in enum]
        super(EnumField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return obj.value

    def to_internal_value(self, data):
        try:
            return self.enum[data]
        except KeyError:
            self.fail('invalid_choice', input=data)


class Base64ImageField(Base64FieldMixin, ImageField):
    # This class get from https://github.com/Hipo/drf-extra-fields/blob/master/drf_extra_fields/fields.py
    """
    A django-rest-framework field for handling image-uploads through raw post data.
    It uses base64 for en-/decoding the contents of the file.
    """

    ALLOWED_TYPES = (
        "jpeg",
        "jpg",
        "png",
    )
    INVALID_FILE_MESSAGE = _("Please upload a valid image.")
    INVALID_TYPE_MESSAGE = _("The type of the image couldn't be determined.")


    def get_file_extension(self, filename, decoded_file):
        try:
            from PIL import Image
        except ImportError:
            raise ImportError("Pillow is not installed.")
        extension = imghdr.what(filename, decoded_file)

        # Try with PIL as fallback if format not detected due
        # to bug in imghdr https://bugs.python.org/issue16512
        if extension is None:
            image = Image.open(io.BytesIO(decoded_file))
            extension = image.format.lower()

        extension = "jpg" if extension == "jpeg" else extension
        return extension
