from washer_project.celery import app


@app.task(name="stores.delete_store_index")
def delete_store_index(store_id):
    from search.indexer import StoreIndexer
    from stores.models import Store

    store = Store.objects.get(pk=store_id)
    store_indexer = StoreIndexer()
    store_indexer.delete_store(store)
