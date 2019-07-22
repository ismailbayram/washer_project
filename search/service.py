from search.documents import StoreDoc


class StoreSearchService:
    def query_stores(self, query_params):
        # TODO: cache by hashing query params

        lat = query_params.get('lat')
        lon = query_params.get('lon')
        distance = query_params.get('distance')
        name = query_params.get('name')
        rating = query_params.get('rating')
        city = query_params.get('city')
        township = query_params.get('township')
        credit_card = query_params.get('credit_card')
        cash = query_params.get('cash')

        response = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        }

        query = StoreDoc.search()
        if name:
            query = query.query("match", name=name)
        if rating and rating.isdigit():
            query = query.filter('range', rating={'gte': int(rating)})
        if lat and lon and distance and distance.isdigit():
            try:
                lat = float(lat)
                lon = float(lon)
                query = query.filter('geo_distance', distance=f'{distance}m', location=[lon, lat])
            except ValueError:
                pass
        if city and city.isdigit():
            query = query.filter('match', city=int(city))
        if township and township.isdigit():
            query = query.filter('match', township=int(township))
        if credit_card:
            credit_card = True if credit_card else False
            query = query.filter('match', credit_card=credit_card)
        if cash:
            cash = True if cash else False
            query = query.filter('match', cash=cash)

        results = query.execute()
        response['count'] = results.hits.total.value
        for hit in results:
            response['results'].append(hit.to_dict())

        return response
