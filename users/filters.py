from django_filters import rest_framework as filters

from users.models import WorkerProfile


class WorkerProfileFilterSet(filters.FilterSet):
    class Meta:
        model = WorkerProfile
        fields = ('store', )
