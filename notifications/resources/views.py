from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from notifications.models import Notification
from notifications.resources.serializers import NotificationSerializer
from users.enums import GroupType


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated, )

    def filter_queryset(self, *args, **kwargs):
        queryset = self.queryset
        profile_type = self.request.META.get("HTTP_X_PROFILE_TYPE")

        if profile_type == GroupType.washer.value:
            object_id = self.request.user.washer_profile.pk
            ct = ContentType.objects.get_for_model(self.request.user.washer_profile)
            queryset = Notification.objects.filter(content_type=ct,
                                                   object_id=object_id)
        elif profile_type == GroupType.customer.value:
            object_id = self.request.user.customer_profile.pk
            ct = ContentType.objects.get_for_model(self.request.user.customer_profile)
            queryset = Notification.objects.filter(content_type=ct,
                                                   object_id=object_id)
        elif profile_type == GroupType.worker.value:
            object_id = self.request.user.worker_profile.pk
            ct = ContentType.objects.get_for_model(self.request.user.worker_profile)
            queryset = Notification.objects.filter(content_type=ct,
                                                   object_id=object_id)
        else:
            # TODO log here
            raise NotFound()

        return super().filter_queryset(queryset)
