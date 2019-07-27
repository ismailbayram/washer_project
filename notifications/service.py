from stores.models import Store
from users.models import WorkerProfile


class NotificationService:
    def create_notification(self, notification_type, data, view, view_id, receiver):
        """
        :param notification_type: NotificationType
        :param data: dict
        :param view: String
        :param view_id: String
        :param receiver: Store, WasherProfile, CustomerProfile, WorkerProfile
        """
        if isinstance(receiver, Store):
            receiver.washer_profile.notifications.create(
                notification_type=notification_type,
                data=data,
                view=view,
                view_id=view_id
            )
            for workerprofile in receiver.workerprofile_set.all():
                workerprofile.notifications.create(
                    notification_type=notification_type,
                    data=data,
                    view=view,
                    view_id=view_id
                )

        else:
            receiver.notifications.create(
                notification_type=notification_type,
                data=data,
                view=view,
                view_id=view_id
            )
