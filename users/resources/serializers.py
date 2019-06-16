from rest_framework import serializers

from api.fields import EnumField
from users.models import User
from users.enums import UserType


class UserSerializer(serializers.ModelSerializer):
    user_type = EnumField(enum=UserType)

    class Meta:
        model = User
        fields = ('pk', 'user_type', 'last_login', 'first_name',
                  'last_name', 'date_joined', 'phone_number', 'is_active')


class AuthFirstStepSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
