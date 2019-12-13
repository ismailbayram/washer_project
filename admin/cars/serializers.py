from rest_framework import serializers

from cars.models import Car
from cars.enums import CarType
from api.fields import EnumField
from admin.users.serializers import CustomerProfileSerializer


class CarSerializer(serializers.ModelSerializer):
    car_type = EnumField(enum=CarType)
    user = CustomerProfileSerializer(source='customer_profile')

    class Meta:
        model = Car
        fields = ('pk', 'user', 'licence_plate', 'car_type', 'is_selected', 'is_active', )
