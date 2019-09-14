from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import NotFound
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from notifications.models import Notification
from notifications.resources.serializers import NotificationSerializer
from notifications.service import NotificationService
from users.enums import GroupType


class NotificationViewSet(ListModelMixin, GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated, )
    service = NotificationService()

    def list(self, request, *args, **kwargs):
        response = super().list(self, request, *args, **kwargs)

        queryset = self.filter_queryset().filter(read=False)
        self.service.set_read_notifications(queryset)

        return response


    def filter_queryset(self, *args, **kwargs):
        queryset = self.queryset
        profile_type = self.request.META.get("HTTP_X_PROFILE_TYPE") # X-Profile-Type

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
