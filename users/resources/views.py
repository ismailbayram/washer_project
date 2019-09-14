from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import HasGroupPermission, IsWasherOrReadOnlyPermission
from stores.models import Store
from users.enums import GroupType
from users.exceptions import ThereIsUserGivenPhone
from users.models import User, WorkerProfile
from users.resources.filters import WorkerProfileFilterSet
from users.resources.serializers import (AuthFirstStepSerializer,
                                         AuthSecondStepSerializer,
                                         ChangePhoneNumberSerializer,
                                         ChangePhoneNumberVerifySerializer,
                                         UserInfoSerializer,
                                         WorkerProfileSerializer)
from users.service import SmsService, UserService, WorkerProfileService


class WorkerProfileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                           mixins.ListModelMixin):
    queryset = WorkerProfile.objects.all()
    filter_class = WorkerProfileFilterSet
    serializer_class = WorkerProfileSerializer
    permission_classes = (HasGroupPermission, IsWasherOrReadOnlyPermission, )
    permission_groups = {
        'create': [GroupType.washer],
        'list': [GroupType.washer],
        'retrieve': [GroupType.washer],
        'update': [],
        'partial_update': [],
        'fire': [GroupType.washer],
        'move': [GroupType.washer]
    }
    service = WorkerProfileService()

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return self.request.user.washer_profile.workerprofile_set.all()

    def perform_create(self, serializer):
        serializer.instance = self.service.create_worker(self.request.user.washer_profile,
                                                         **serializer.validated_data)

    @action(detail=True, methods=['POST'])
    def fire(self, request, *args, **kwargs):
        worker_profile = self.get_object()
        self.service.fire_worker(worker_profile)
        return Response({}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='move/(?P<store_pk>[0-9]+)')
    def move(self, request, store_pk=None, *args, **kwargs):
        worker_profile = self.get_object()
        store = get_object_or_404(Store, pk=store_pk, washer_profile=request.user.washer_profile)
        self.service.move_worker(worker_profile, store)
        return Response({}, status=status.HTTP_200_OK)


class AuthView(APIView):
    def post(self, request):
        serializer = AuthFirstStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_service = UserService()
        sms_service = SmsService()

        sms_obj = sms_service.get_or_create_sms_code(
            phone_number=serializer.validated_data.get('phone_number')
        )

        user_service.get_or_create_user(**serializer.validated_data)

        # TODO send real sms
        return Response({}, status=status.HTTP_200_OK)


class SmsVerifyView(APIView):
    def post(self, request):
        serializer = AuthSecondStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_service = UserService()
        sms_service = SmsService()

        sms_service.verify_sms(**serializer.validated_data)

        _, token = user_service.get_or_create_user(**serializer.validated_data)

        return Response({'token':token})


class UserInfoView(APIView):
    serializer_class = UserInfoSerializer
    permission_classes = (IsAuthenticated, )
    service = UserService

    def get(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        instance = self.request.user

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = self.service()
        service.change_user_names(user=instance, **serializer.validated_data)

        _, token = service.get_or_create_user(phone_number=instance.phone_number)

        return Response({**serializer.validated_data, 'token': token})


class ChangePhoneNumberRequestView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ChangePhoneNumberSerializer

    def post(self, request, *args, **kwargs):
        """
        -> :token: (user)
        -> :param: phone_number
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if (User.objects.filter(phone_number=
                                serializer.validated_data.get('phone_number')).exists()):
            raise ThereIsUserGivenPhone

        sms_service = SmsService()
        sms_instance = sms_service.get_or_create_sms_code(**serializer.validated_data)
        # TODO send real sms
        return Response({}, status=status.HTTP_200_OK)


class ChangePhoneNumberSmsVerifyView(APIView):
    permission_classes = (IsAuthenticated, )
    service = SmsService()
    serializer_class = ChangePhoneNumberVerifySerializer

    def post(self, request, *args, **kwargs):
        """
        -> :token: (user)
        -> :param: phone_number
        -> :param: sms_code
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.service.verify_sms_when_change_phone(user=request.user, **serializer.validated_data)
        user_service = UserService()
        user, token = user_service.get_or_create_user(phone_number=serializer.validated_data.get('phone_number'))

        return Response({'token':token})
