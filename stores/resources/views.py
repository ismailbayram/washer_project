from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import HasGroupPermission, IsWasherOrReadOnlyPermission
from address.service import AddressService
from address.resources.serializers import AddressSerializer
from users.enums import GroupType
from stores.resources.serializers import StoreSerializer
from stores.models import Store
from stores.service import StoreService


class StoreViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin, mixins.UpdateModelMixin,
                   mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Store.objects.prefetch_stores()
    serializer_class = StoreSerializer
    permission_classes = (HasGroupPermission, IsWasherOrReadOnlyPermission,)
    permission_groups = {
        'create': [GroupType.washer],
        'update': [GroupType.washer],
        'list': [GroupType.washer],
        'partial_update': [],
        'retrieve': [GroupType.washer],
        'approve': [],
        'decline': [],
        'address': [GroupType.washer]
    }

    # TODO: add activate action
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(washer_profile=self.request.user.washer_profile)

    def perform_create(self, serializer):
        service = StoreService()
        data = serializer.validated_data
        data.update({
            "washer_profile": self.request.user.washer_profile,
        })
        serializer.instance = service.create_store(**data)

    def perform_update(self, serializer):
        service = StoreService()
        store = self.get_object()
        serializer.instance = service.update_store(store, **serializer.validated_data)

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
        serializer.instance = service.create_address(store, **serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StoreListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.filter(is_active=True, is_approved=True)\
                            .select_related('address')
    # TODO: connect with google maps
    serializer_class = StoreSerializer
