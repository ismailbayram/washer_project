import elasticsearch_dsl as es

from django.conf import settings


class StoreDoc(es.Document):
    pk = es.Integer()
    name = es.Text()
    location = es.GeoPoint()
    rating = es.Float()
    city = es.Integer()
    township = es.Integer()
    credit_card = es.Boolean()
    cash = es.Boolean()

    class Index:
        name = settings.ES_STORE_INDEX
        settings = {
            "number_of_shards": 2
        }
