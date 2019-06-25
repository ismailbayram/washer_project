from rest_framework import serializers

from address.resources.serializers import AddressSerializer
from stores.models import Store


class StoreSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Store
        fields = ('name', 'address', 'longitude', 'latitude', 'rating')
