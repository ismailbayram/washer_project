import elasticsearch_dsl as es


class StoreDoc(es.Document):
    pk = es.Integer()
    name = es.Text()
    latitude = es.Float()
    longitude = es.Float()
    rating = es.Float()

    class Index:
        name = 'stores'
        settings = {
            "number_of_shards": 2
        }
