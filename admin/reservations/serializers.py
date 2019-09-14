from rest_framework import serializers

from reservations.models import CancellationReason


class CancellationReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationReason
        fields = "__all__"
