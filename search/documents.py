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


class ReservationDoc(es.Document):
    pk = es.Integer()
    period = es.Integer()
    status = es.Text()
    start_datetime = es.Date()
    end_datetime = es.Date()
    store = es.Nested(StoreDoc)

    class Index:
        name = settings.ES_RESERVATION_INDEX
        settings = {
            "number_of_shards": 2
        }
