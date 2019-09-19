from rest_framework import serializers

from cars.models import Car
from cars.enums import CarType
from api.fields import EnumField
from users.models import User


class CustomerProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone_number = serializers.CharField(source='user.phone_number')

    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'phone_number')


class CarSerializer(serializers.ModelSerializer):
    car_type = EnumField(enum=CarType)
    user = CustomerProfileSerializer(source='customer_profile')

    class Meta:
        model = Car
        fields = ('pk', 'user', 'licence_plate', 'car_type', 'is_selected', 'is_active', )
