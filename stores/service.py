from stores.models import Store


class StoreService():
    def create_store(self, name, washer_profile, phone_number, tax_office,
                     tax_number, latitude=None, longitude=None):
        store = Store.objects.create(name=name, washer_profile=washer_profile,
                                     phone_number=phone_number, tax_office=tax_office,
                                     tax_number=tax_number, latitude=latitude, longitude=longitude)

        return store

    def approve_store(self, instance):
        """
        :param instance: Store
        :return: Store
        """
        # TODO: send notification
        instance.is_approved = True
        instance.save(update_fields=['is_approved'])
        return instance

    def decline_store(self, instance):
        """
        :param instance: Store
        :return: Store
        """
        # TODO: send notification
        instance.is_approved = False
        instance.save(update_fields=['is_approved'])
        return instance

    # TODO: config
