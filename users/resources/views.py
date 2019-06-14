from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.negotiation import DefaultContentNegotiation

from users.resources.serializers import UserSerializer
from users.models import User


class UserViewSet(ModelViewSet):
    # TODO: exclude admin users
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AuthView(APIView):
    def post(self, request):
        import ipdb
        ipdb.set_trace()
        return Response({}, status=status.HTTP_200_OK)
