from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sentence = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ("pk", "sentence", 'view', 'view_id', )

    def get_sentence(self, instance):
        return instance.notification_type.get_sentence(instance.data)
