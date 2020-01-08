import datetime

from rest_framework import serializers

from address.resources.serializers import AddressDetailedSerializer
from admin.stores.service import AdminStoreService
from admin.users.serializers import WasherProfileSerializer
from reservations.enums import ReservationStatus
from reservations.models import Comment
from reservations.resources.serializers import CommentSerializer
from stores.models import Store
from stores.resources.serializers import (StoreImagesWithSizesSerializer,
                                          StoreSerializer)
from users.resources.serializers import WorkerProfileSerializer


class StoreAdminDetailedSerializer(StoreSerializer):
    images = StoreImagesWithSizesSerializer(many=True, read_only=True)
    washer_profile = WasherProfileSerializer(read_only=True)
    worker_profiles = serializers.SerializerMethodField()
    last_comments = serializers.SerializerMethodField()
    period = serializers.SerializerMethodField()
    weekly_reservation_count = serializers.SerializerMethodField()

    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + (
            'weekly_reservation_count', 'created_date', 'modified_date',
            'images', 'logo',
            'worker_profiles',
            'last_comments', 'period',
        )
        extra_kwargs = {
            'created_date': {'read_only': True},
            'modified_date': {'read_only': True},
            'logo': {'read_only': True},
            'name': {'read_only': True},
            'phone_number': {'read_only': True},
            'latitude': {'read_only': True},
            'longitude': {'read_only': True},
            'tax_office': {'read_only': True},
            'tax_number': {'read_only': True},
            'address': {'read_only': True},
            'rating': {'read_only': True},
            'config': {'read_only': True},
            'is_active': {'read_only': True},
            'is_approved': {'read_only': True},
            'payment_options': {'read_only': True}
        }

    def get_weekly_reservation_count(self, obj):
        return AdminStoreService().get_weekly_reservation_count(obj)

    def get_last_comments(self, obj):
        last_five_comment = Comment.objects.filter(
            reservation__in=obj.reservation_set.filter(
                status=ReservationStatus.completed,
                comment__isnull=False
            )
        )[:5]

        return CommentSerializer(last_five_comment, many=True).data

    def get_worker_profiles(self, obj):
        return WorkerProfileSerializer(obj.workerprofile_set, many=True).data

    def get_period(self, obj):
        return obj.get_primary_product().period


class StoreSimpleSerializer(serializers.ModelSerializer):
    address = AddressDetailedSerializer()

    class Meta:
        model = Store
        fields = ('pk', 'name', 'washer_profile', 'phone_number', 'latitude', 'longitude',
                  'tax_office', 'tax_number', 'address', 'rating', 'config', 'is_active',
                  'is_approved', 'payment_options')
