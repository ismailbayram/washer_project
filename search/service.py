from django.conf import settings

from search.documents import StoreDoc, ReservationDoc
from search.resources.serializers import (StoreFilterSerializer,
                                          ReservationFilterSerializer)


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
        if 'rating__gte' in data:
            query = query.filter('range', rating={'gte': data['rating__gte']})
        if 'city' in data:
            query = query.filter('match', city=data['city'])
        if 'township' in data:
            query = query.filter('match', township=data['township'])
        if 'credit_card' in data:
            query = query.filter('match', credit_card=data['credit_card'])
        if 'cash' in data:
            query = query.filter('match', cash=data['cash'])
        if 'location' in data:
            query = query.filter('geo_distance', distance=f'{data["distance"]}{serializer.distance_metric}',
                                 location=data['location'])
        if 'search_text' in data:
            query = query.query("match", search_text=data['search_text'])

        if 'sort' in data:
            query = query.sort(data['sort'])

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
    def query_reservations(self, query_params):
        """
        :param query_params: QueryDict
        :return: function
        """
        serializer = ReservationFilterSerializer(data=query_params)
        if not serializer.is_valid():
            # TODO: Log here
            print('LOG HERE!')

        data = serializer.validated_data
        # TODO: cache by hashing query params: hash(data)
        query = ReservationDoc.search()

        if "store" in data:
            query = query.filter({
                "match": {"store.pk": data["store"]}
            })
        if "rating__gte" in data:
            query = query.filter({
                "range": {"store.rating": {"gte": data["rating__gte"]}}
            })
        if "city" in data:
            query = query.filter({
                "match": {"store.city": data["city"]}
            })
        if "township" in data:
            query = query.filter({
                "match": {"store.township": data["township"]}
            })
        if "credit_card" in data:
            query = query.filter({
                "match": {"store.credit_card": data["credit_card"]}
            })
        if "cash" in data:
            query = query.filter({
                "match": {"store.cash": data["cash"]}
            })
        if "start_datetime__lte" in data:
            # example: 2019-07-24T23:59:00.002308%2B03:00
            query = query.filter('range', start_datetime={"lte": data['start_datetime__lte']})
        if "start_datetime__gte" in data:
            query = query.filter('range', start_datetime={"gte": data['start_datetime__gte']})
        if "car_type" in data:
            car_type = data['car_type'].value
            query = query.filter({
                "range": {f"price.{car_type}": {"gte": data['price__gte'],
                                                "lte": data['price__lte']}}
            })

        query = query.sort(data.get('sort', 'start_datetime'))

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
