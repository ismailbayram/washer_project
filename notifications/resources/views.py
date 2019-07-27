from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from notifications.exceptions import BadUserProfileHeaderException
from notifications.models import Notification
from notifications.resources.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated, )

    def filter_queryset(self, *args, **kwargs):
        queryset = self.queryset
        profile_type = self.request.META.get("HTTP_X_PROFILE_TYPE")

        if profile_type not in ('washer', 'customer', 'worker'):
            raise BadUserProfileHeaderException

        if profile_type == 'washer':
            queryset = queryset.filter(washer_profile=self.request.user.washer_profile)
        elif profile_type == 'customer':
            queryset = queryset.filter(customer_profile=self.request.user.customer_profile)
        elif profile_type == 'worker':
            queryset = queryset.filter(worker_profile=self.request.user.worker_profile)

        return super().filter_queryset(queryset)
