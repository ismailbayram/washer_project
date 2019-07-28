from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.transaction import atomic
from PIL import Image

from base.utils import (compress_image, ordereddict_to_dict,
                        thumbnail_file_name_by_orginal_name)
from notifications.enums import NotificationType
from notifications.service import NotificationService
from products.service import ProductService
from stores.exceptions import (ImageDidNotDelete, StoreHasNoLogo,
                               StoreHasSoManyImageException)
from stores.models import Store, StoreImageItem
from stores.tasks import delete_store_index


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
        payment_options = {'credit_card': False, 'cash': True}
        store = Store.objects.create(name=name, washer_profile=washer_profile,
                                     phone_number=phone_number, tax_office=tax_office, config=config,
                                     tax_number=tax_number, latitude=latitude, longitude=longitude,
                                     payment_options=payment_options)
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
        payment_options = kwargs.get('payment_options', None)
        update_fields = ['name', 'phone_number', 'tax_office', 'tax_number']
        declined = False

        if latitude:
            store.latitude = latitude
            update_fields.append('latitude')
            declined = True
        if longitude:
            store.longitude = longitude
            update_fields.append('longitude')
            declined = True
        if not store.phone_number == phone_number:
            declined = True
        if is_active is not None:
            store.is_active = is_active
            update_fields.append('is_active')

        if config:
            store.config = ordereddict_to_dict(config)
            update_fields.append('config')

        if payment_options:
            store.payment_options = ordereddict_to_dict(payment_options)
            update_fields.append('payment_options')

        with atomic():
            # TODO: if declined send notification to admin
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
        instance.is_approved = True
        instance.save(update_fields=['is_approved'])

        notif_service = NotificationService()
        notif_service.send(instance=instance, to=instance.washer_profile,
                           notif_type=NotificationType.reservation_started,)

        return instance

    def decline_store(self, instance):
        """
        :param instance: Store
        :return: Store
        """
        # TODO: check reservations
        instance.is_approved = False
        instance.save(update_fields=['is_approved'])
        delete_store_index.delay(instance.id)
        return instance

    # def activate_store(self, instance):
    #     """
    #     :param instance: Store
    #     :return: Store
    #     """
    #     # NOT AVAILABLE FOR NOW
    #     instance.is_active = True
    #     instance.save(update_fields=['is_active'])
    #     create_store_weekly_reservations.delay(instance.id)
    #     return instance

    # def deactivate_store(self, instance):
    #     """
    #     :param instance: Store
    #     :return: Store
    #     """
    #     # NOT AVAILABLE FOR NOW
    #     instance.is_active = False
    #     instance.save(update_fields=['is_active'])
    #     return instance

    def add_logo(self, store, logo):
        """
        :param store: Store
        :param logo: ContentFile
        :return: store
        """

        # If there is logo allready it need to be delete on as a file
        if store.logo:
            default_storage.delete(store.logo.name)

        image = compress_image(logo, do_square=True)
        store.logo = image
        store.save()
        return store

    def delete_logo(self, store):
        """
        :param store: Store
        """
        if not store.logo:
            raise StoreHasNoLogo
        default_storage.delete(store.logo.name)
        store.logo = None
        store.save()

    def add_image(self, store, image, washer_profile):
        """
        :param store: Store
        :param image: ContentFile
        :param washer_profile: WasherProfile
        """
        if StoreImageItem.objects.filter(store=store).count() > 9:
            raise StoreHasSoManyImageException

        image = compress_image(image, do_square=True)  # Compress the comming image

        # Save StoreImageItem model
        saved_image = StoreImageItem.objects.create(store=store, image=image,
                                                    washer_profile=washer_profile)
        saved_name_ext = saved_image.image.name.split(".")[-1]

        # Saving thumbnail images
        pil_image = Image.open(saved_image.image)
        edge_size = min(pil_image.size)
        for name, size in settings.IMAGE_SIZES.items():
            croped_image = pil_image.crop((0, 0, edge_size, edge_size))
            croped_image.thumbnail((size['height'], size['width'],), Image.ANTIALIAS)

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
            store_image_item.delete()
        except:
            raise ImageDidNotDelete

        default_storage.delete(store_image_item.image.name)
        for name, _ in settings.IMAGE_SIZES.items():
            default_storage.delete(
                thumbnail_file_name_by_orginal_name(store_image_item.image.name, name)
            )
