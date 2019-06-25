from stores.models import Store


class StoreService():
    def deactivate_store(self, instance):
        """
        :param instance: Store
        :return: Store
        """
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return instance
