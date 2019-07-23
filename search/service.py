from django.conf import settings
from django.core.paginator import PageNotAnInteger, EmptyPage

from search.documents import StoreDoc
from search.paginator import ESPaginator
from search.resources.serializers import StoreFilterSerializer


class StoreSearchService:
    def query_stores(self, query_params):
        # TODO: sorters
        serializer = StoreFilterSerializer(data=query_params)
        if not serializer.is_valid():
            # TODO: Log here
            print('LOG HERE!')

        data = serializer.validated_data
        page = data.get('page', 1)
        limit = data.get('limit', settings.REST_FRAMEWORK['PAGE_SIZE'])
        # TODO: cache by hashing query params: hash(data)

        import ipdb
        ipdb.set_trace()

        response = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        }

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

        start = (page - 1) * limit
        end = start + limit
        count = query.count()
        if count < end:
            end = count
            start = end - limit

        query = query[start:end]
        results = query.execute()
        paginator = ESPaginator(results, limit)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        response['count'] = paginator._count.value
        for hit in results.object_list:
            response['results'].append(hit.to_dict())

        return response
