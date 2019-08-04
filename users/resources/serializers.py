from rest_framework import serializers

from api.fields import EnumField
from api.validators import is_valid_phone
from users.enums import GroupType
from users.models import User, WorkerProfile


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('pk', 'date_joined', 'last_login', 'first_name', 'last_name',
                  'phone_number', 'is_active', 'is_customer', 'is_washer',
                  'is_worker')


class WorkerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = WorkerProfile
        fields = ('pk', 'washer_profile', 'store', 'user', 'first_name',
                  'last_name', 'phone_number')
        extra_kwargs = {
            'store': {'required': True},
        }

class AuthFirstStepSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[is_valid_phone])
    group_type = EnumField(enum=GroupType)




class AuthSecondStepSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    sms_code = serializers.CharField()
    group_type = EnumField(enum=GroupType)
