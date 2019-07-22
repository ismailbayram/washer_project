from rest_framework import serializers

from stores.models import Store


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
