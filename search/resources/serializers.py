from rest_framework import serializers

from api.fields import EnumField
from stores.models import Store
from reservations.models import Reservation
from reservations.enums import ReservationStatus


class StoreDocumentSerializer(serializers.ModelSerializer):
    city = serializers.IntegerField(source='address.city.pk')
    township = serializers.IntegerField(source='address.township.pk')
    location = serializers.SerializerMethodField()
    credit_card = serializers.BooleanField(default=False)
    cash = serializers.BooleanField(default=True)

    class Meta:
        model = Store
        fields = ('pk', 'name', 'location', 'rating', 'city', 'township',
                  'credit_card', 'cash')
        extra_kwargs = {
            'rating': {'default': 0}
        }

    def get_location(self, instance):
        latitude = instance.latitude
        longitude = instance.longitude
        return {
            'lat': latitude,
            'lon': longitude
        }


class ReservationDocumentSerializer(serializers.ModelSerializer):
    status = EnumField(enum=ReservationStatus)
    store = StoreDocumentSerializer()

    class Meta:
        model = Reservation
        fields = ('pk', 'period', 'status', 'start_datetime', 'end_datetime',
                  'store')


class StoreFilterSerializer(serializers.Serializer):
    name = serializers.CharField()
    location = serializers.ListField()
    distance = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        self.distance_metric = kwargs.get('distance_metric', 'm')

    def validate(self, attrs):
        lat = attrs.get('lat', None)
        lon = attrs.get('lon', None)
        distance = attrs.get('distance', None)

        if not lat and lon and distance:
            attrs.pop('lat', None)
            attrs.pop('lon', None)
            attrs.pop('distance', None)

        return attrs
