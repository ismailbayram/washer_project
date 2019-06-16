from rest_framework import status
from rest_framework_jwt.settings import api_settings as jwt_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import permissions

from users.resources.serializers import (UserSerializer, AuthFirstStepSerializer)
from users.models import User


class UserViewSet(ModelViewSet):
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )


class AuthView(APIView):
    def post(self, request):
        serializer = AuthFirstStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jwt_response_payload_handler = jwt_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = jwt_settings.JWT_ENCODE_HANDLER
        user = User.objects.get(phone_number=serializer.validated_data['phone_number'])

        payload = jwt_response_payload_handler(user)

        return Response({'token': jwt_encode_handler(payload)}, status=status.HTTP_200_OK)
