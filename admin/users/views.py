from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from admin.users.serializers import LoginSerializer, UserSerializer
from users.models import User
from users.service import UserService
from admin.users.filters import UserFilterSet


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('groups').all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )
    filter_class = UserFilterSet

    def perform_destroy(self, instance):
        service = UserService()
        service.deactivate_user(instance)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data.get('username'), is_staff=True)
            pw_check = user.check_password(data.get('password'))
            if not pw_check:
                raise ValidationError({
                    "non_field_errors": [_('Username or password is incorrect')]
                })
            user_service = UserService()
            token = user_service._create_token(user)
            return Response({
                'token': 'Token {}'.format(token)
            })
        except User.DoesNotExist:
            raise ValidationError({
                "non_field_errors": [_('Username or password is incorrect')]
            })
