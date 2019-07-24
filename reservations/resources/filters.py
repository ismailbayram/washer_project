from django_filters import rest_framework as filters

from reservations.models import Comment, Reservation


class ReservationFilterSet(filters.FilterSet):
    class Meta:
        model = Reservation
        fields = ('store', 'status')

class CommentFilterSet(filters.FilterSet):
    store = filters.NumberFilter('reservation__store')

    class Meta:
        model = Comment
        fields = ('store', )
