from notifications.enums import NotificationType
from stores.models import Store
from users.models import WorkerProfile


class NotificationService:
    def _create_notification(self, notification_type, data, view, view_id, receiver):
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

    def send(self, instance, notif_type, to, *args, **kwargs):
        view = notif_type.get_view()
        if notif_type in [NotificationType.you_fired, NotificationType.you_are_fired]:
            data = {
                "worker_name": "{} {}".format(instance.user.first_name, instance.user.last_name),
                "washer_name": instance.washer_profile.user.first_name,
                "worker_profile_id": instance.id,
                "washer_profile_id": instance.washer_profile.id,
            }
            view_id = instance.id

        elif notif_type in [NotificationType.you_moved_worker_to_store,
                            NotificationType.you_are_moved_another_store]:
            data = {
                "worker_name": "{} {}".format(instance.user.first_name, instance.user.last_name),
                "store_name": instance.washer_profile.store.name,
                "store_id": instance.washer_profile.store.id,
                "worker_profile_id": instance.id,
            }
            view_id = instance.washer_profile.store.id,

        elif notif_type == NotificationType.you_has_new_worker:

            data = {
                "worker_name": "{} {}".format(instance.user.first_name, instance.user.last_name),
                "worker_profile_id": instance.id,
            }
            view_id = instance.id,

        else:
            raise NotImplementedError()

        self._create_notification(notification_type=notif_type, data=data, view=view,
                                  view_id=view_id, receiver=to)

        # TODO push notification triger


    def set_read_notifications(self, notifications):
        """
        :param notification: QuerySet<Notification>
        """
        notifications.update(is_readed=True)
