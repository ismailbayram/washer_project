from rest_framework import views, status
from rest_framework.response import Response

from search.service import StoreSearchService


class ReservationSearchView(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_200_OK)


class StoreSearchView(views.APIView):
    service = StoreSearchService()

    def get(self, request, *args, **kwargs):
        count, results = self.service.query_stores(request.query_params)
        response = {
            'count': count,
            'results': results
        }
        return Response(response, status=status.HTTP_200_OK)

