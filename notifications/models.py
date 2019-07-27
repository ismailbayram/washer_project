from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from enumfields import EnumField

from base.models import StarterModel
from notifications.enums import NotificationType


class Notification(StarterModel):
    notification_type = EnumField(enum=NotificationType, max_length=32)
    data = JSONField(default=dict)
    view = models.CharField(max_length=32)
    view_id = models.CharField(max_length=32)
    read = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return self.notification_type.value
