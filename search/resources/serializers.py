from rest_framework import serializers

from django.conf import settings

from api.fields import EnumField
from cars.enums import CarType
from stores.models import Store
from reservations.models import Reservation
from reservations.enums import ReservationStatus


class StoreDocumentSerializer(serializers.ModelSerializer):
    search_text = serializers.SerializerMethodField()
    city = serializers.IntegerField(source='address.city.pk')
    township = serializers.IntegerField(source='address.township.pk')
    location = serializers.SerializerMethodField()
    credit_card = serializers.BooleanField(default=False)
    cash = serializers.BooleanField(default=True)

    class Meta:
        model = Store
        fields = ('pk', 'name', 'search_text', 'location', 'rating', 'city', 'township',
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

    def get_search_text(self, instance):
        return f'{instance.name} {instance.address.city.name} {instance.address.township.name}'


class ReservationDocumentSerializer(serializers.ModelSerializer):
    status = EnumField(enum=ReservationStatus)
    store = StoreDocumentSerializer()

    class Meta:
        model = Reservation
        fields = ('pk', 'period', 'status', 'start_datetime', 'end_datetime', 'store')


class StoreFilterSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=False)
    search_text = serializers.CharField(required=False)
    distance = serializers.IntegerField(required=False)
    top_left_lat = serializers.FloatField(required=False)
    top_left_lon = serializers.FloatField(required=False)
    bottom_right_lat = serializers.FloatField(required=False)
    bottom_right_lon = serializers.FloatField(required=False)
    city = serializers.IntegerField(required=False)
    township = serializers.IntegerField(required=False)
    rating__gte = serializers.FloatField(required=False)
    credit_card = serializers.NullBooleanField(required=False)
    cash = serializers.NullBooleanField(required=False)
    limit = serializers.IntegerField(default=settings.REST_FRAMEWORK['PAGE_SIZE'])
    page = serializers.IntegerField(default=1)
    sort = serializers.CharField(required=False)

    def validate_page(self, page):
        if page < 1:
            page = 1
        return page

    def validate_sort(self, sort):
        if not sort in ['-rating', 'rating']:
            return
        return sort

    def validate(self, attrs):
        top_left_lat = attrs.get('top_left_lat', None)
        top_left_lon = attrs.get('top_left_lon', None)
        bottom_right_lat = attrs.get('bottom_right_lat', None)
        bottom_right_lon = attrs.get('bottom_right_lon', None)

        if not (top_left_lat and top_left_lon and bottom_right_lat and bottom_right_lon):
            attrs.pop('top_left_lat', None)
            attrs.pop('top_left_lon', None)
            attrs.pop('bottom_right_lat', None)
            attrs.pop('bottom_right_lon', None)

        return attrs


class ReservationFilterSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=False)
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
