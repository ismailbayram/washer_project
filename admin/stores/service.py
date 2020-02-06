import datetime

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

    def get_weekly_reservation_count(self, instance):
        period = instance.get_primary_product().period

        count = 0
        for day_name in ('monday', 'sunday', 'tuesday', 'wednesday',
                         'thursday', 'friday', 'saturday'):
            try:
                start = instance.config['reservation_hours'][day_name]['start']
                end = instance.config['reservation_hours'][day_name]['end']
            except KeyError:
                continue

            if start and end and end > start:
                start_delta = datetime.timedelta(
                    hours=int(start.split(":")[0]), minutes=int(start.split(":")[1])
                )
                end_delta = datetime.timedelta(
                    hours=int(end.split(":")[0]), minutes=int(end.split(":")[1])
                )
                total_minute = ((end_delta - start_delta).total_seconds())/60
                count += total_minute//period

        return count
