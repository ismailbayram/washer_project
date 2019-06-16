from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from api.permissions import IsAdminUser

from users.resources.serializers import (UserSerializer, AuthFirstStepSerializer)
from users.models import User
from users.service import UserService


class UserViewSet(ModelViewSet):
    """
       Users Resources

       list:
           Get a list of User Objects.
           Sample list response body;
           <br/>

           {
            "count": 1,
            "next": null,
            "previous": null,
            "results": [
                    {
                        "pk": 3,
                        "user_type": "normal",
                        "last_login": null,
                        "first_name": "ahmet",
                        "last_name": "cetin",
                        "date_joined": "2019-06-16T17:46:21.225910+03:00",
                        "phone_number": "+905423037159"
                    },
                    ...
                ]
            }


       retrieve:
           Get a single User object with given id.
           Successful retrieve response body sample;
           <br/>

           {
                "pk": 3,
                "user_type": "normal",
                "last_login": null,
                "first_name": "ahmet",
                "last_name": "cetin",
                "date_joined": "2019-06-16T17:46:21.225910+03:00",
                "phone_number": "+905423037159",
                "is_active': True
            }

       <br/>
       If User object does not found with given id, then you will get
       status code; **404_NOT_FOUND** and response body like;
       <br/>

           {
               "detail": "Not found."
           }

       create:
           Create a new User object with given json data.
           If object successfully created, then you will get
           status code; **201_CREATED** and created object in response body.

       destroy:
           Deactivate a given User object.
           If object successfully deactivated, then you will get
           status code; **204_NO_CONTENT**.

       """
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )

    def perform_destroy(self, instance):
        service = UserService()
        instance = service.deactivate_user(instance)
        return instance


class AuthView(APIView):
    """
       Auth Resources
       create:
           Create a new Channel object with given json data.
           If object successfully created, then you will get
           status code; **201_CREATED** and created object in response body.

       """
    def post(self, request):
        serializer = AuthFirstStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = UserService()
        token = service.create_token(**serializer.validated_data)
        return Response({'token': token}, status=status.HTTP_200_OK)
