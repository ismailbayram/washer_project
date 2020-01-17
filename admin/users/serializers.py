from rest_framework import serializers

from users.models import User, WasherProfile, CustomerProfile, WorkerProfile, WorkerJobLog
from stores.resources.serializers import StoreSerializer


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
        fields = ('pk', 'user',)


class WasherProfileSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = WasherProfile


class WorkerProfileSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = WorkerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = CustomerProfile


class WorkerJobLogSerializer(serializers.ModelSerializer):
    worker_profile = WorkerProfileSerializer(read_only=True)
    store = StoreSerializer(read_only=True)

    class Meta:
        model = WorkerJobLog
        fields = ('pk', 'worker_profile', 'store', 'start_date',
                  'end_date',)
