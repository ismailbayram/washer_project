from elasticsearch_dsl import connections

from django.apps import AppConfig
from django.conf import settings


class SearchConfig(AppConfig):
    name = 'search'

    def ready(self):
        connections.create_connection(hosts=[settings.ES_HOST], timeout=60)
        from search.documents import StoreDoc, ReservationDoc
        StoreDoc.init()
        ReservationDoc.init()
