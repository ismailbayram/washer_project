from django.db.transaction import atomic

from base.utils import ordereddict_to_dict
from stores.models import Store
from products.service import ProductService


class StoreService:
    @atomic
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
        config = {'opening_hours': {}, 'reservation_hours': {}}
        store = Store.objects.create(name=name, washer_profile=washer_profile,
                                     phone_number=phone_number, tax_office=tax_office, config=config,
                                     tax_number=tax_number, latitude=latitude, longitude=longitude)
        product_service = ProductService()
        product_service.create_primary_product(store)
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
            store.latitude = latitude
            update_fields.append('latitude')
            store.is_approved = False
            update_fields.append('is_approved')

        if longitude:
            store.longitude = longitude
            update_fields.append('longitude')
            store.is_approved = False
            update_fields.append('is_approved')

        if not store.phone_number == phone_number:
            store.is_approved = False
            update_fields.append('is_approved')

        if is_active is not None:
            store.is_active = is_active
            update_fields.append('is_active')

        if config:
            store.config = ordereddict_to_dict(config)
            update_fields.append('config')

        store.name = name
        store.phone_number = phone_number
        store.tax_office = tax_office
        store.tax_number = tax_number
        store.save(update_fields=[*set(update_fields)])

        return store

    def approve_store(self, instance):
        """
        :param instance: Store
        :return: Store
        """
        # NOTIFICATION
        instance.is_approved = True
        instance.save(update_fields=['is_approved'])
        return instance

    def decline_store(self, instance):
        """
        :param instance: Store
        :return: Store
        """
        # NOTIFICATION
        instance.is_approved = False
        instance.save(update_fields=['is_approved'])
        return instance
