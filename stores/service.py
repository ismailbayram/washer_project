from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.transaction import atomic
from PIL import Image
from rest_framework import exceptions

from base.utils import ordereddict_to_dict, thumbnail_file_name_by_orginal_name
from products.service import ProductService
from stores.exceptions import ImageDidNotDelete, StoreHasSoManyImageException
from stores.models import Store, StoreImageItem


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

    def add_logo(self, store, washer_profile):
        pass

    def add_image(self, store, image, washer_profile):
        """
        :param store: Store
        :param image: ContentFile
        :param washer_profile: WasherProfile
        """
        if StoreImageItem.objects.filter(store=store).count() > 9:
            raise StoreHasSoManyImageException

        # Compress the comming image
        not_saved_pure_name = "".join(image.name.split('.')[0:-1])
        pil_image = Image.open(image)
        pil_image.convert('RGB')

        f = BytesIO()
        pil_image.save(f, "JPEG", quality=90)
        image = ContentFile(f.getvalue())
        image.name = "{0}.{1}".format(not_saved_pure_name, "jpeg")

        # Save StoreImageItem model
        saved_image = StoreImageItem.objects.create(
            store=store,
            image=image,
            washer_profile=washer_profile
        )
        saved_name_ext = saved_image.image.name.split(".")[-1]

        # Saving thumbnail images
        pil_image = Image.open(saved_image.image)
        edge_size = min(pil_image.size)
        for name, size in settings.IMAGE_SIZES.items():
            croped_image = pil_image.crop((0, 0, edge_size, edge_size))

            croped_image.thumbnail(
                (size['height'], size['width'],),
                Image.ANTIALIAS
            )

            # pillow image to ContentFile and save
            f = BytesIO()
            croped_image.save(f, saved_name_ext)
            default_storage.save(
                thumbnail_file_name_by_orginal_name(saved_image.image.name, name),
                ContentFile(f.getvalue())
            )

    def delete_image(self, store_image_item, washer_profile):
        """
        :param store_image_item: StoreImageItem
        :param washer_profeile: WasherProfile
        :return: boolean
        """
        try:
            count, _ = store_image_item.delete()
        except:
            raise ImageDidNotDelete

        default_storage.delete(store_image_item.image.name)
        for name, _ in settings.IMAGE_SIZES.items():
            default_storage.delete(
                thumbnail_file_name_by_orginal_name(store_image_item.image.name, name)
            )
