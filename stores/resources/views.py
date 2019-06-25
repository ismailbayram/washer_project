from rest_framework import viewsets

from api.permissions import HasGroupPermission
from users.enums import GroupType
from stores.resources.serializers import StoreSerializer
from stores.models import Store
from stores.service import StoreService


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.filter(is_active=True, is_approved=True)\
                            .select_related('address', 'address__city',
                                            'address__township')
    serializer_class = StoreSerializer
    permission_classes = (HasGroupPermission, )
    permission_groups = {
        'create': [GroupType.washer],
        'update': [GroupType.washer],
        'partial_update': [GroupType.washer],
        'destroy': [GroupType.washer]
    }
    service = StoreService
