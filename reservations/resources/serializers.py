from rest_framework import serializers

from api.fields import EnumField
from stores.resources.serializers import StoreSerializer
from reservations.models import Reservation
from reservations.enums import ReservationStatus


class ReservationSerializer(serializers.ModelSerializer):
    status = EnumField(enum=ReservationStatus)
    store = StoreSerializer()

    class Meta:
        model = Reservation
        fields = ('pk', 'number', 'start_datetime', 'end_datetime', 'period', 'store', 'status')
