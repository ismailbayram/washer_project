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

        if profile_type not in (GroupType.worker.value, GroupType.customer.value, GroupType.washer.value):
            # TODO log here
            raise NotFound()

        if profile_type == GroupType.washer.value:
            queryset = queryset.filter(washer_profile=self.request.user.washer_profile)
        elif profile_type == GroupType.customer.value:
            queryset = queryset.filter(customer_profile=self.request.user.customer_profile)
        elif profile_type == GroupType.worker.value:
            queryset = queryset.filter(worker_profile=self.request.user.worker_profile)

        return super().filter_queryset(queryset)
