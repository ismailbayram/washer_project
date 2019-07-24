from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from address.resources.serializers import AddressSerializer
from address.service import AddressService
from api.permissions import (HasGroupPermission, IsWasherOrReadOnlyPermission,
                             ReadOnly)
from reservations.models import Comment
from reservations.resources.serializers import CommentSerializer
from stores.models import Store, StoreImageItem
from stores.resources.serializers import (StoreImageSerializer,
                                          StoreLogoSerializer, StoreSerializer)
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
        'address': [GroupType.washer],
        'add-image': [GroupType.washer],
        'delete-image': [GroupType.washer],
        'logo': [GroupType.washer],
        # 'comments'
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

    @action(detail=True, methods=['POST'], url_path='photo_gallery')
    def add_image(self, request, *args, **kwargs):
        service = StoreService()
        serializer = StoreImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service.add_image(**data, store=self.get_object(),
                          washer_profile=request.user.washer_profile)

        return Response({}, status=status.HTTP_202_ACCEPTED)


    @action(detail=True, methods=['DELETE'], url_path='photo_gallery/(?P<image_pk>[0-9]+)')
    def delete_image(self, request, image_pk=None, *args, **kwargs):
        service = StoreService()
        store_image_item = get_object_or_404(StoreImageItem, pk=image_pk,
                                             washer_profile=request.user.washer_profile)
        service.delete_image(store_image_item, request.user.washer_profile)
        return Response({}, status=status.HTTP_202_ACCEPTED)


    @action(detail=True, methods=['POST', 'DELETE'], url_path='logo')
    def logo(self, request, *args, **kwargs):
        if request.method == 'POST':
            service = StoreService()
            serializer = StoreLogoSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            service.add_logo(**data, store=self.get_object())
            return Response({}, status=status.HTTP_202_ACCEPTED)
        if request.method == 'DELETE':
            service = StoreService()
            service.delete_logo(self.get_object())
            return Response({}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['GET'], url_path='comments', permission_classes=(ReadOnly, ))
    def comments(self, request, *args, **kwargs):

        store = get_object_or_404(Store, pk=self.kwargs['pk'])
        print(
            Comment.objects.filter(reservation__in=store.reservation_set.all()).count()
        )
        serializer = CommentSerializer(
            Comment.objects.filter(reservation__in=store.reservation_set.all()),
            many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class StoreListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.filter(is_active=True, is_approved=True)\
                            .select_related('address')
    # TODO: connect with google maps
    serializer_class = StoreSerializer
