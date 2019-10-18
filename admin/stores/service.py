from admin.stores.exceptions import StoreIsAlreadyApproved, StoreIsAlreadyDeclined

from notifications.enums import NotificationType
from notifications.service import NotificationService

from stores.tasks import delete_store_index


class AdminStoreService:
    def approve_store(self, instance):
        """
        :param instance: Store
        :return: Store
        """
        if instance.is_approved:
            raise StoreIsAlreadyApproved
        instance.is_approved = True
        instance.save(update_fields=['is_approved'])

        notif_service = NotificationService()
        notif_service.send(instance=instance, to=instance.washer_profile,
                           notif_type=NotificationType.store_approved)

        return instance

    def decline_store(self, instance):
        """
        :param instance: Store
        :return: Store
        """
        if not instance.is_approved:
            raise StoreIsAlreadyDeclined

        instance.is_approved = False
        instance.save(update_fields=['is_approved'])
        delete_store_index.delay(instance.id)
        return instance
