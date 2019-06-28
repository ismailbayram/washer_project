from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from address.resources.serializers import AddressDetailedSerializer
from stores.models import Store


class DaySerializer(serializers.Serializer):
    start = serializers.TimeField(format="[HH:[MM]]", allow_null=True)
    end = serializers.TimeField(format="[HH:[MM]]", allow_null=True)
    # TODO: test

    def validate(self, attrs):
        start = attrs['start']
        end = attrs['end']

        if (start and not end) or (not start and end):
            raise ValidationError(_('Başlangıç ve bitiş saatleri verilmeli.'))

        return attrs


class WeekSerializer(serializers.Serializer):
    monday = DaySerializer()
    tuesday = DaySerializer()
    wednesday = DaySerializer()
    thursday = DaySerializer()
    friday = DaySerializer()
    saturday = DaySerializer()
    sunday = DaySerializer()


class OpeningHoursSerializer(WeekSerializer):
    pass


class ReservationHoursSerializer(WeekSerializer):
    pass


class ConfigSerializer(serializers.Serializer):
    opening_hours = OpeningHoursSerializer(default={})
    reservation_hours = ReservationHoursSerializer(default={})


class StoreSerializer(serializers.ModelSerializer):
    address = AddressDetailedSerializer(read_only=True)
    rating = serializers.ReadOnlyField()
    is_approved = serializers.ReadOnlyField()
    washer_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    config = ConfigSerializer()

    class Meta:
        model = Store
        fields = ('pk', 'name', 'washer_profile', 'phone_number', 'latitude', 'longitude',
                  'tax_office', 'tax_number', 'address', 'rating', 'config', 'is_active',
                  'is_approved')
