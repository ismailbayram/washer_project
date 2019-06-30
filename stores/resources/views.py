from rest_framework import viewsets, views, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import HasGroupPermission, IsOwnerOrReadOnlyPermission
from address.service import AddressService
from address.resources.serializers import AddressSerializer
from users.enums import GroupType
from stores.resources.serializers import StoreSerializer
from stores.models import Store
from stores.service import StoreService


class StoreViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin, mixins.UpdateModelMixin,
                   mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = (HasGroupPermission, IsOwnerOrReadOnlyPermission, )
    permission_groups = {
        'create': [GroupType.washer],
        'update': [GroupType.washer],
        'list': [GroupType.washer],
        'partial_update': [],
        'deactivate': [GroupType.washer],
        'activate': [GroupType.washer],
        'retrieve': [GroupType.washer],
        'approve': [],
        'decline': [],
    }

    def perform_create(self, serializer):
        service = StoreService()
        instance = service.create_store(washer_profile=self.request.user.washer_profile,
                                        **serializer.validated_data)
        return instance

    def perform_update(self, serializer):
        service = StoreService()
        store = self.get_object()
        instance = service.update_store(store, **serializer.validated_data)
        # FIXME: it shows old data after updating
        return instance

    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
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
    def address(self, request, *args, **kwargs):
        service = AddressService()
        store = self.get_object()
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service.create_address(store, **serializer.validated_data)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class StoreListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.filter(is_active=True, is_approved=True)\
                            .select_related('address')
    # TODO: compare select_related address and other address fields
    # TODO: connect with google maps
    serializer_class = StoreSerializer
