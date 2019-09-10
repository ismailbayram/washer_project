from django_filters import rest_framework as filters

from users.models import User


class UserFilterSet(filters.FilterSet):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        # 'is_customer', 'is_worker', 'is_washer'
