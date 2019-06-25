from rest_framework import viewsets, views, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import HasGroupPermission
from api.views import MultiSerializerViewMixin
from users.enums import GroupType
from stores.resources.serializers import StoreSerializer, StoreDetailedSerializer
from stores.models import Store
from stores.service import StoreService


class StoreViewSet(MultiSerializerViewMixin, viewsets.GenericViewSet,
                   mixins.CreateModelMixin, mixins.UpdateModelMixin,
                   mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    action_serializers = {
        'retrieve': StoreDetailedSerializer,
        'list': StoreDetailedSerializer,
    }
    permission_classes = (HasGroupPermission, )
    permission_groups = {
        'create': [GroupType.washer],
        'update': [GroupType.washer],
        'list': [GroupType.washer],
        'partial_update': [GroupType.washer],
        'deactivate': [GroupType.washer],
        'activate': [GroupType.washer],
        'approve': [],
        'decline': [],
    }

    def perform_create(self, serializer):
        service = StoreService()
        instance = service.create_store(washer_profile=self.request.user.washer_profile,
                                        **serializer.validated_data)
        return instance

    def list(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return super().list(request, *args, **kwargs)
        self.queryset = request.user.washer_profile.store_set.all()
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['POST'])
    def approve(self, request, *args, **kwargs):
        service = StoreService()
        instance = self.get_object()
        service.approve_store(instance)
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def decline(self, request, *args, **kwargs):
        service = StoreService()
        instance = self.get_object()
        service.decline_store(instance)
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def activate(self, request, *args, **kwargs):
        service = StoreService()
        instance = self.get_object()
        service.activate_store(instance)
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def deactivate(self, request, *args, **kwargs):
        service = StoreService()
        instance = self.get_object()
        service.deactivate_store(instance)
        return Response({}, status=status.HTTP_200_OK)

    # TODO: add checking object permission


class StoreListView(views.APIView):
    def get(self):
        # TODO: ElasticSearch
        queryset = Store.objects.filter(is_active=True, is_approved=True) \
            .select_related('address', 'address__city',
                            'address__township')
        pass
