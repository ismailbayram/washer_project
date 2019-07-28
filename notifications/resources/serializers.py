from rest_framework import serializers

from api.fields import EnumField
from notifications.enums import NotificationType
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sentence = serializers.SerializerMethodField()
    notification_type = EnumField(enum=NotificationType)

    class Meta:
        model = Notification
        fields = ("pk", "sentence", 'view', 'view_id', 'notification_type')

    def get_sentence(self, instance):
        return instance.notification_type.get_sentence(instance.data)
