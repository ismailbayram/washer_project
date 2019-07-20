from stores.models import Store
from search.documents import StoreDoc
from search.resources.serializers import StoreDocumentSerializer


class StoreIndexService:
    def index_store(self, store):
        """
        :param store: Store
        :return: None
        """
        serializer = StoreDocumentSerializer(instance=store)
        doc = StoreDoc(**serializer.data)
        doc.meta.id = store.pk
        doc.save(index=StoreDoc.Index.name)

    def index_stores(self):
        """
        :return: None
        """
        for store in Store.objects.filter(is_approved=True, is_active=True)\
                .select_related('address', 'address__city', 'address__township'):
            self.index_store(store)

    def delete_store(self, store):
        """
        :param store: Store
        :return: None
        """
        doc = StoreDoc()
        doc.delete(id=store.pk)
