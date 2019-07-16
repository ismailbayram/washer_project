from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from address.resources.serializers import AddressDetailedSerializer
from api.fields import Base64ImageField
from base.utils import thumbnail_file_name_by_orginal_name
from stores.models import Store, StoreImageItem


class DaySerializer(serializers.Serializer):
    start = serializers.TimeField(format="[HH:[MM]]", default=None, allow_null=True)
    end = serializers.TimeField(format="[HH:[MM]]", default=None, allow_null=True)

    def validate(self, attrs):
        start = attrs.get('start', None)
        end = attrs.get('end', None)

        if (start and not end) or (not start and end):
            raise ValidationError(_('Başlangıç ve bitiş saatleri birlikte verilmeli.'))

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
    pass


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
                raise ValidationError(_('Dükkanın kapalı olduğu günlerde randevu açılamaz.'))
            if reservation_hours[day]["start"] < hours["start"]:
                raise ValidationError(_('Randevu saatleri dükkan açılış saatinden sonra olmalı.'))
            if reservation_hours[day]["end"] > hours["end"]:
                raise ValidationError(_('Randevu saatleri dükkan kapanış saatinden önce olmalı.'))

        return attrs


class StoreImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)

    class Meta:
        model = StoreImageItem
        fields = ('pk', 'image', )


class StoreImagesWithSizesSerializer(serializers.RelatedField):
    def to_representation(self, obj):
        images = {'full': obj.image.url}
        for name, _ in settings.IMAGE_SIZES.items():
            images[name] = thumbnail_file_name_by_orginal_name(obj.image.url, name)
        return {"pk":obj.pk, "image":images}


class StoreSerializer(serializers.ModelSerializer):
    address = AddressDetailedSerializer(read_only=True)
    rating = serializers.ReadOnlyField()
    is_approved = serializers.ReadOnlyField()
    washer_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    config = ConfigSerializer(default={}, partial=False)
    images = StoreImagesWithSizesSerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ( 'images','pk', 'name', 'washer_profile', 'phone_number', 'latitude', 'longitude',
                  'tax_office', 'tax_number', 'address', 'rating', 'config', 'is_active',
                  'is_approved',)



class StoreDetailedSerializer(StoreSerializer):
    # workerprofile_set =

    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + ('created_date', 'modified_date',
                                                'workerprofile_set')
