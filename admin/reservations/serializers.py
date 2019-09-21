from rest_framework import serializers

from reservations.models import CancellationReason


class CancellationReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationReason
        fields = ('pk', 'reason', 'is_active',
                  'created_date', 'modified_date', )
