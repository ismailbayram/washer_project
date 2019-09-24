from rest_framework import serializers

from stores.models import Store


class StoreSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('pk', 'name', 'washer_profile', 'phone_number', 'latitude', 'longitude',
                  'tax_office', 'tax_number', 'address', 'rating', 'config', 'is_active',
                  'is_approved', 'payment_options')
