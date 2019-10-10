from rest_framework import serializers

from api.fields import EnumField
from admin.stores.serializers import StoreSimpleSerializer
from baskets.resources.serializers import BasketSerializer
from stores.resources.serializers import StoreSerializer
from reservations.enums import ReservationStatus
from reservations.models import Reservation
from reservations.models import CancellationReason
from reservations.resources.serializers import CommentSerializer
from admin.cars.serializers import CustomerProfileSerializer


class CancellationReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationReason
        fields = ('pk', 'reason', 'is_active',
                  'created_date', 'modified_date', )


class ReservationDetailedSerializer(serializers.ModelSerializer):
    status = EnumField(enum=ReservationStatus)
    store = StoreSimpleSerializer()
    comment = CommentSerializer()
    cancellation_reason = CancellationReasonSerializer()
    basket = BasketSerializer()

    class Meta:
        model = Reservation
        fields = (
            'pk', 'number', 'comment', 'start_datetime', 'end_datetime',
            'period', 'store', 'status', 'cancellation_reason', 'basket',
        )


class ReservationSerializer(serializers.ModelSerializer):
    status = EnumField(enum=ReservationStatus)
    store = StoreSerializer()
    comment = CommentSerializer()
    cancellation_reason = CancellationReasonSerializer()
    customer_profile = CustomerProfileSerializer()

    class Meta:
        model = Reservation
        fields = (
            'pk', 'number', 'comment', 'start_datetime', 'end_datetime',
            'period', 'store', 'status', 'cancellation_reason',
            'customer_profile',
        )
