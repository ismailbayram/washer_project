from stores.models import Store


class StoreService:
    def create_store(self, name, washer_profile, phone_number, tax_office,
                     tax_number, latitude=None, longitude=None, **kwargs):
        """
        :param name: str
        :param washer_profile: WasherProfile
        :param phone_number: str
        :param tax_office: str
        :param tax_number: str
        :param latitude: float
        :param longitude: float
        :param kwargs: dict
        :return: Store
        """
        store = Store.objects.create(name=name, washer_profile=washer_profile,
                                     phone_number=phone_number, tax_office=tax_office,
                                     tax_number=tax_number, latitude=latitude, longitude=longitude)

        return store

    def update_store(self, store, name, phone_number, tax_office, tax_number, **kwargs):
        """
        :param store: Store
        :param name: str
        :param phone_number: str
        :param tax_office: str
        :param tax_number: str
        :param kwargs: dict
        :return: Store
        """
        latitude = kwargs.get('latitude', None)
        longitude = kwargs.get('longitude', None)
        is_active = kwargs.get('is_active', None)
        config = kwargs.get('config', None)
        update_fields = ['name', 'phone_number', 'tax_office', 'tax_number']

        if latitude:
            update_fields.append('latitude')
            store.latitude = latitude

        if longitude:
            update_fields.append('longitude')
            store.longitude = longitude

        if latitude or longitude or not store.phone_number == phone_number:
            store.is_approved = False

        if is_active:
            update_fields.append('is_active')
            store.is_active = is_active

        store.name = name
        store.phone_number = phone_number
        store.tax_office = tax_office
        store.tax_number = tax_number
        store.save(update_fields=update_fields)

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
