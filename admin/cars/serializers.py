from rest_framework import serializers

from cars.models import Car
from cars.enums import CarType
from api.fields import EnumField
from users.models import CustomerProfile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'phone_number',)
        extra_kwargs = {
            'phone_number': {'read_only': True},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
        }


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = User
        fields = ('user', )


class CarSerializer(serializers.ModelSerializer):
    car_type = EnumField(enum=CarType)
    customer_profile = CustomerProfileSerializer()

    class Meta:
        model = Car
        fields = ('pk', 'customer_profile', 'licence_plate', 'car_type', 'is_selected', 'is_active', )
