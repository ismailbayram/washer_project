from rest_framework import serializers

from api.fields import EnumField
from reservations.enums import ReservationStatus
from reservations.models import Comment, Reservation
from stores.resources.serializers import StoreSerializer


class CommentSerializer(serializers.ModelSerializer):
    raiting = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Comment
        fields = ('pk', 'raiting', 'comment', 'reservation', 'reply', )
        read_only_fields = ('reply', 'reservation',)

class ReplySerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('reply',)
        extra_kwargs = {'reply': {'required': True}}


class ReservationSerializer(serializers.ModelSerializer):
    status = EnumField(enum=ReservationStatus)
    store = StoreSerializer()
    comment = CommentSerializer()

    class Meta:
        model = Reservation
        fields = ('pk', 'number','comment', 'start_datetime', 'end_datetime', 'period', 'store', 'status')
