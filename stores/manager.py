from django.db.models.manager import Manager


class StoreManager(Manager):
    def prefetch_stores(self):
        return self.select_related('address__country', 'address__city',
                                    'address__township')
