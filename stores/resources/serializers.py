from rest_framework import serializers

from address.resources.serializers import AddressSerializer
from stores.models import Store


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = ('pk', 'name', 'washer_profile', 'phone_number', 'longitude', 'latitude',
                  'tax_office', 'tax_number')


class StoreDetailedSerializer(StoreSerializer):
    address = AddressSerializer()
    is_approved = serializers.ReadOnlyField()

    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + ('address', 'rating', 'config',
                                                'is_active', 'is_approved')
