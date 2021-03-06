import datetime

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from address.resources.serializers import AddressDetailedSerializer
from api.fields import Base64ImageField
from api.validators import is_valid_phone
from base.utils import thumbnail_file_name_by_orginal_name
from stores.models import Store, StoreImageItem


class DaySerializer(serializers.Serializer):
    start = serializers.TimeField(format="[HH:[MM]]", default=None, allow_null=True)
    end = serializers.TimeField(format="[HH:[MM]]", default=None, allow_null=True)

    def validate(self, attrs):
        start = attrs.get('start', None)
        end = attrs.get('end', None)

        if (start and not end) or (not start and end):
            raise ValidationError(_('You have to input start and end times together'))

        if start and end:
            if start >= end:
                raise ValidationError(_('Start time must be before the end time.'))
            start_time = datetime.datetime.strptime(start, "%H:%M")
            end_time = datetime.datetime.strptime(end, "%H:%M")
            diff = (end_time - start_time).seconds / 60

            if diff <= 59:
                raise ValidationError(_('The start time must be at least 1 hour between the end time.'))

        return attrs

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value['start']:
            value['start'] = value['start'].strftime("%H:%M")
        if value['end']:
            value['end'] = value['end'].strftime("%H:%M")
        return value


class WeekSerializer(serializers.Serializer):
    monday = DaySerializer()
    tuesday = DaySerializer()
    wednesday = DaySerializer()
    thursday = DaySerializer()
    friday = DaySerializer()
    saturday = DaySerializer()
    sunday = DaySerializer()

    def to_representation(self, instance):
        if not instance:
            return {}
        return super().to_representation(instance)


class OpeningHoursSerializer(WeekSerializer):
    pass


class ReservationHoursSerializer(WeekSerializer):
    pass


class PaymentOptionsSerializer(serializers.Serializer):
    credit_card = serializers.BooleanField(required=True)
    cash = serializers.BooleanField(required=True)

    def to_representation(self, instance):
        if not instance:
            return {'credit_card': False, 'cash': True}
        return super().to_representation(instance)

    def validate(self, attrs):
        credit_card = attrs.get('credit_card')
        cash = attrs.get('cash')

        if not (credit_card or cash):
            raise ValidationError(_("At least one of payment options must be available."))

        return attrs


class ConfigSerializer(serializers.Serializer):
    opening_hours = OpeningHoursSerializer()
    reservation_hours = ReservationHoursSerializer()

    def to_representation(self, instance):
        if not instance:
            return {'opening_hours': {}, 'reservation_hours': {}}
        return super().to_representation(instance)

    def validate(self, attrs):
        opening_hours = attrs['opening_hours']
        reservation_hours = attrs['reservation_hours']
        for day, hours in opening_hours.items():
            if reservation_hours[day]["start"] is None and hours['start'] is None:
                continue
            if reservation_hours[day]["start"] is not None and hours['start'] is None:
                raise ValidationError(_('Reservations cannot be opened on the days when the car wash is closed.'))
            if reservation_hours[day]["start"] < hours["start"]:
                raise ValidationError(_('Reservation hours must be between opening and closing hours.'))
            if reservation_hours[day]["end"] > hours["end"]:
                raise ValidationError(_('Reservation hours must be between opening and closing hours.'))

        return attrs


class StoreImageSerializer(serializers.Serializer):
    image = Base64ImageField(required=True, allow_empty_file=False)

    class Meta:
        model = StoreImageItem
        fields = ('pk', 'image', )


class StoreLogoSerializer(serializers.ModelSerializer):
    logo = Base64ImageField(required=True, allow_empty_file=False)

    class Meta:
        model = Store
        fields = ('logo', )


class StoreImagesWithSizesSerializer(serializers.RelatedField):
    def to_representation(self, obj):
        request = self.context.get('request')

        images = {
            'full': request.build_absolute_uri(obj.image.url)
        }
        for name, _ in settings.IMAGE_SIZES.items():
            images[name] = thumbnail_file_name_by_orginal_name(
                request.build_absolute_uri(obj.image.url),
                name
            )
        return {"pk": obj.pk, "image": images}


class StoreSerializer(serializers.ModelSerializer):
    address = AddressDetailedSerializer(read_only=True)
    washer_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    config = ConfigSerializer(default=dict, partial=False)
    payment_options = PaymentOptionsSerializer(default=dict, partial=False)

    class Meta:
        model = Store
        fields = ('pk', 'name', 'washer_profile', 'phone_number', 'latitude', 'longitude',
                  'tax_office', 'tax_number', 'address', 'rating', 'config', 'is_active',
                  'is_approved', 'payment_options')
        extra_kwargs = {
            'rating': {'read_only': True},
            'is_active': {'read_only': True},
            'is_approved': {'read_only': True},
            'phone_number': {'validators': [is_valid_phone]},
        }


class StoreDetailedSerializer(StoreSerializer):
    images = StoreImagesWithSizesSerializer(many=True, read_only=True)

    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + ('created_date', 'modified_date',
                                                'images', 'logo', )
