from rest_framework import serializers

from stores.models import Store


class StoreDocumentSerializer(serializers.ModelSerializer):
    city = serializers.IntegerField(source='address.city.pk')
    township = serializers.IntegerField(source='address.township.pk')

    class Meta:
        model = Store
        fields = ('pk', 'name', 'latitude', 'longitude', 'rating', 'city', 'township')
