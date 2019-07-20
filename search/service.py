from stores.models import Store
from search.documents import StoreDoc
from search.resources.serializers import StoreDocumentSerializer


class StoreIndexService:
    def index_store(self, store):
        serializer = StoreDocumentSerializer(instance=store)
        doc = StoreDoc(**serializer.data)
        doc.meta.id = store.pk
        doc.save(index=StoreDoc.Index.name)

    def index_stores(self):
        for store in Store.objects.filter(is_approved=True, is_active=True):
            self.index_store(store)
