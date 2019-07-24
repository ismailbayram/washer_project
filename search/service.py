from django.conf import settings

from search.documents import StoreDoc
from search.resources.serializers import StoreFilterSerializer


class StoreSearchService:
    def query_stores(self, query_params):
        """
        :param query_params: QueryDict
        :return: function
        """
        serializer = StoreFilterSerializer(data=query_params)
        if not serializer.is_valid():
            # TODO: Log here
            print('LOG HERE!')

        data = serializer.validated_data
        # TODO: cache by hashing query params: hash(data)

        query = StoreDoc.search()
        if 'name' in data:
            query = query.query("match", name=data['name'])
        if 'rating' in data:
            query = query.filter('range', rating={'gte': data['rating']})
        if 'location' in data:
            query = query.filter('geo_distance', distance=f'{data["distance"]}{serializer.distance_metric}',
                                 location=data['location'])
        if 'city' in data:
            query = query.filter('match', city=data['city'])
        if 'township' in data:
            query = query.filter('match', township=data['township'])
        if 'credit_card' in data:
            query = query.filter('match', credit_card=data['credit_card'])
        if 'cash' in data:
            query = query.filter('match', cash=data['cash'])

        query = query.sort(data['sort'], '-rating')

        return self._paginate_response(query, data.get('page'), data.get('limit'))

    def _paginate_response(self, query, page, limit):
        """
        :param query: ESSearch
        :param page: int
        :param limit: int
        :return: dict
        """
        page = page or 1
        limit = limit or settings.REST_FRAMEWORK['PAGE_SIZE']

        start = (page - 1) * limit
        end = start + limit

        count = query.count()
        query = query[start:end]
        response = query.execute()

        results = []
        for hit in response:
            results.append(hit.to_dict())

        return count, results


class ReservationSearchService:
    # TODO: filter by primary product price
    pass
