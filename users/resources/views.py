from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from api.permissions import IsAdminUser

from users.resources.serializers import (UserSerializer, AuthFirstStepSerializer)
from users.models import User
from users.service import UserService


class UserViewSet(ModelViewSet):
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )


class AuthView(APIView):
    def post(self, request):
        serializer = AuthFirstStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = UserService()
        token = service.create_token(**serializer.validated_data)
        return Response({'token': token}, status=status.HTTP_200_OK)
