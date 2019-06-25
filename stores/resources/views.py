from rest_framework import viewsets, views

from api.permissions import HasGroupPermission
from users.enums import GroupType
from stores.resources.serializers import StoreSerializer
from stores.models import Store
from stores.service import StoreService


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = (HasGroupPermission, )
    permission_groups = {
        'create': [GroupType.washer],
        'update': [GroupType.washer],
        'list': [GroupType.washer],
        'partial_update': [GroupType.washer],
        'destroy': [GroupType.washer]
    }

    def list(self, request, *args, **kwargs):
        import ipdb
        ipdb.set_trace()
        if request.user.is_staff:
            return super().list(request, *args, **kwargs)
        self.queryset = self.get_queryset().filter(washer_profile=request.user.washer_profile)
        return super().list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        service = StoreService()
        return service.deactivate_store(instance)

    # TODO: activate action
    # TODO: approve action only admin users
    # TODO: add checking object permission


class StoreListView(views.APIView):
    def get(self):
        # TODO: ElasticSearch
        queryset = Store.objects.filter(is_active=True, is_approved=True) \
            .select_related('address', 'address__city',
                            'address__township')
        pass
