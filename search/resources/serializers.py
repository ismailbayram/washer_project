from rest_framework import serializers

from django.conf import settings

from api.fields import EnumField
from cars.enums import CarType
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
        fields = ('pk', 'period', 'status', 'start_datetime', 'end_datetime', 'store')


class StoreFilterSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    distance = serializers.IntegerField(required=False)
    lat = serializers.FloatField(required=False)
    lon = serializers.FloatField(required=False)
    location = serializers.ListField(read_only=True)
    city = serializers.IntegerField(required=False)
    township = serializers.IntegerField(required=False)
    rating__gte = serializers.FloatField(required=False)
    credit_card = serializers.NullBooleanField(required=False)
    cash = serializers.NullBooleanField(required=False)
    limit = serializers.IntegerField(default=settings.REST_FRAMEWORK['PAGE_SIZE'])
    page = serializers.IntegerField(default=1)
    sort = serializers.CharField(default='-rating')

    def __init__(self, *args, **kwargs):
        self.distance_metric = kwargs.get('distance_metric', 'm')
        super().__init__(*args, **kwargs)

    def validate_page(self, page):
        if page < 1:
            page = 1
        return page

    def validate_sort(self, sort):
        if not sort in ['-rating', 'rating']:
            return '-rating'
        return sort

    def validate(self, attrs):
        lat = attrs.get('lat', None)
        lon = attrs.get('lon', None)
        distance = attrs.get('distance', None)

        if not (lat and lon and distance):
            attrs.pop('lat', None)
            attrs.pop('lon', None)
            attrs.pop('distance', None)
        else:
            attrs['location'] = [lon, lat]

        return attrs


class ReservationFilterSerializer(serializers.Serializer):
    store = serializers.IntegerField(required=False)
    city = serializers.IntegerField(required=False)
    township = serializers.IntegerField(required=False)
    rating__gte = serializers.FloatField(required=False)
    credit_card = serializers.NullBooleanField(required=False)
    cash = serializers.NullBooleanField(required=False)
    limit = serializers.IntegerField(default=settings.REST_FRAMEWORK['PAGE_SIZE'])
    page = serializers.IntegerField(default=1)
    sort = serializers.CharField(default='start_datetime')
    start_datetime__lte = serializers.DateTimeField(required=False)
    start_datetime__gte = serializers.DateTimeField(required=False)
    price__lte = serializers.FloatField(required=False)
    price__gte = serializers.FloatField(required=False)
    car_type = EnumField(enum=CarType, required=False)

    def validate_page(self, page):
        if page < 1:
            page = 1
        return page

    def validate_sort(self, sort):
        sortings = {
            'rating': 'store.rating',
            '-rating': '-store.rating',
            'start_datetime': 'start_datetime',
            '-start_datetime': '-start_datetime',
        }
        for car_type, label in CarType.choices():
            sortings[f'price_{car_type}'] = f'price.{car_type}'
            sortings[f'-price_{car_type}'] = f'-price.{car_type}'
        try:
            return sortings[sort]
        except KeyError:
            return 'start_datetime'

    def validate(self, attrs):
        price__lte = attrs.get('price__lte', None)
        price__gte = attrs.get('price__gte', None)
        car_type = attrs.get('car_type', None)

        if not (price__lte and car_type and price__gte):
            attrs.pop('price__gte', None)
            attrs.pop('price__lte', None)
            attrs.pop('car_type', None)

        return attrs
