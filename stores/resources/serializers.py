from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from address.resources.serializers import AddressDetailedSerializer
from stores.models import Store


class DaySerializer(serializers.Serializer):
    start = serializers.TimeField(format="[HH:[MM]]", default=None, allow_null=True)
    end = serializers.TimeField(format="[HH:[MM]]", default=None, allow_null=True)
    # TODO: test

    def validate(self, attrs):
        start = attrs.get('start', None)
        end = attrs.get('end', None)

        if (start and not end) or (not start and end):
            raise ValidationError(_('Başlangıç ve bitiş saatleri verilmeli.'))

        if start and end:
            if start >= end:
                raise ValidationError(_('Başlangıç saati bitiş saatinden önce olmalı.'))

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
    # TODO: validate through opening hours
    pass


class ConfigSerializer(serializers.Serializer):
    opening_hours = OpeningHoursSerializer()
    reservation_hours = ReservationHoursSerializer()

    def to_representation(self, instance):
        if not instance:
            return {'opening_hours': {}, 'reservation_hours': {}}
        return super().to_representation(instance)


class StoreSerializer(serializers.ModelSerializer):
    address = AddressDetailedSerializer(read_only=True)
    rating = serializers.ReadOnlyField()
    is_approved = serializers.ReadOnlyField()
    washer_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    config = ConfigSerializer(default={}, partial=False)

    class Meta:
        model = Store
        fields = ('pk', 'name', 'washer_profile', 'phone_number', 'latitude', 'longitude',
                  'tax_office', 'tax_number', 'address', 'rating', 'config', 'is_active',
                  'is_approved')

# TODO: StoreDetailedSerializer -> {modified and created datetime}
