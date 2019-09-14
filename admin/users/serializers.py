from rest_framework import serializers

from users.models import User


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
