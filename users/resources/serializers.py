from rest_framework import serializers

from api.fields import EnumField
from users.models import User
from users.enums import UserType


class UserSerializer(serializers.ModelSerializer):
    user_type = EnumField(enum=UserType)

    class Meta:
        model = User
        fields = '__all__'
