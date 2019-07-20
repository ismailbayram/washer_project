from rest_framework import views, status
from rest_framework.response import Response


class ReservationSearchView(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_200_OK)


class StoreSearchView(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_200_OK)

