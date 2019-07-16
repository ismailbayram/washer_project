from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from address.resources.serializers import AddressSerializer
from address.service import AddressService
from api.permissions import HasGroupPermission, IsWasherOrReadOnlyPermission
from stores.models import Store
from stores.resources.serializers import StoreImageSerializer, StoreSerializer
from stores.service import StoreService
from users.enums import GroupType


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

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return self.request.user.washer_profile.store_set.all()

    def perform_create(self, serializer):
        service = StoreService()
        serializer.instance = service.create_store(washer_profile=self.request.user.washer_profile,
                                        **serializer.validated_data)

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

    @action(detail=True, methods=['POST'], url_path='photo_galery')
    def get_images(self, request, *args, **kwargs):
        print(request.data)
        service = StoreService()
        serializer = StoreImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service.add_image(
            store=self.get_object(),
            image=data['image'],
            washer_profile=request.user.washer_profile
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class StoreListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.filter(is_active=True, is_approved=True)\
                            .select_related('address')
    # TODO: connect with google maps
    serializer_class = StoreSerializer
