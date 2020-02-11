from rest_framework import serializers

from api.fields import EnumField
from reservations.enums import ReservationStatus
from reservations.models import Comment, Reservation, CancellationReason
from stores.resources.serializers import StoreSerializer


class CommentSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=10)
    protected_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('pk', 'rating', 'comment', 'reservation', 'reply', 'protected_name')
        read_only_fields = ('reply', 'reservation',)

    def get_protected_name(self, obj):
        try:
            protected_name = obj.reservation.customer_profile.user.protected_name
        except AttributeError:
            protected_name = ''
        return protected_name


class ReplySerializer(serializers.Serializer):
    reply = serializers.CharField(max_length=255)


class CancellationReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationReason
        fields = ('pk', 'reason')


class ReservationSerializer(serializers.ModelSerializer):
    status = EnumField(enum=ReservationStatus)
    store = StoreSerializer()
    comment = CommentSerializer()
    cancellation_reason = CancellationReasonSerializer()

    class Meta:
        model = Reservation
        fields = (
            'pk', 'number', 'comment', 'start_datetime', 'end_datetime',
            'period', 'store', 'status', 'cancellation_reason',
        )


class CancelReservationSerializer(serializers.ModelSerializer):
    status = EnumField(enum=ReservationStatus, read_only=True)
    store = StoreSerializer(read_only=True)
    comment = CommentSerializer(read_only=True)
    cancellation_reason = serializers.PrimaryKeyRelatedField(
        queryset=CancellationReason.objects.filter(is_active=True)
    )

    class Meta:
        model = Reservation
        fields = (
            'pk', 'number', 'comment', 'start_datetime', 'end_datetime',
            'period', 'store', 'status', 'cancellation_reason',
        )

        extra_kwargs = {
            'cancellation_reason': {'required': True},
            'number': {'read_only': True},
            'start_datetime': {'read_only': True},
            'end_datetime': {'read_only': True},
            'period': {'read_only': True},
            'status': {'read_only': True},
        }
