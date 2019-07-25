import elasticsearch_dsl as es

from django.conf import settings


class StoreDoc(es.Document):
    pk = es.Integer()
    name = es.Text()
    search_text = es.Text()
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
    start_datetime = es.Date(default_timezone=settings.TIME_ZONE)
    end_datetime = es.Date(default_timezone=settings.TIME_ZONE)
    store = es.Object()
    price = es.Object()

    class Index:
        name = settings.ES_RESERVATION_INDEX
        settings = {
            "number_of_shards": 2
        }
