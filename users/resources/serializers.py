from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('pk', 'date_joined', 'last_login', 'first_name',
                  'last_name', 'phone_number', 'is_active')


class AuthFirstStepSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
