from rest_framework import serializers

from address.resources.serializers import AddressSerializer
from stores.models import Store


class StoreSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    rating = serializers.ReadOnlyField()
    is_approved = serializers.ReadOnlyField()
    washer_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    # TODO: config serializer

    class Meta:
        model = Store
        fields = ('pk', 'name', 'washer_profile', 'phone_number', 'latitude', 'longitude',
                  'tax_office', 'tax_number', 'address', 'rating', 'config', 'is_active',
                  'is_approved')
