from rest_framework import serializers

from api.validators import is_valid_phone
from users.models import User, WasherProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'date_joined', 'last_login', 'first_name', 'last_name',
                  'phone_number', 'is_active', 'is_customer', 'is_washer',
                  'is_worker')
        extra_kwargs = {
            'phone_number': {'read_only': True},
            'date_joined': {'read_only': True},
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class BaseProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WasherProfile
        fields = ('pk', 'user',)


class WasherProfileSerializer(BaseProfileSerializer):
    pass
