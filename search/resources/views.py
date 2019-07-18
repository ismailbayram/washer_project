from rest_framework import views, status, viewsets
from rest_framework.response import Response

from stores.models import Store
from stores.resources.serializers import StoreSerializer


class ReservationSearchView(views.APIView):
    def get(self, request, *args, **kwargs):
        # TODO: elasticsearch
        return Response({}, status=status.HTTP_200_OK)


class StoreListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.filter(is_active=True, is_approved=True)\
                            .select_related('address')
    # TODO: connect with google maps
    serializer_class = StoreSerializer

