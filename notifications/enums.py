from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class NotificationType(Enum):
    you_fired = 'you_fired'  # [to washer] you fired someone
    you_are_fired = 'you_are_fired'  # [to worker]
    you_are_moved_another_store = 'you_are_moved_another_store' # [to worker]
    you_moved_worker_to_store = 'you_moved_worker_to_store' # [to washer]
    you_has_new_worker = "you_has_new_worker" # [to washer]

    def get_view(self):
        view_map = {
            'you_fired': 'profile',
            'you_are_fired': 'profile',
            'you_are_moved_another_store': 'store',
            'you_moved_worker_to_store': 'store',
            'you_has_new_worker': 'profile',
        }

        try:
            return view_map[self.value]
        except KeyError:
            raise NotImplementedError()


    def get_sentence(self, data):
        if self.value == 'you_are_moved_another_store':
            return _('Your store is changed to {store_name}.'.format(**data))

        if self.value == 'you_moved_worker_to_store':
            return _('You moved your {worker_name}orker to ({store_name}).'.format(**data))

        if self.value == 'you_fired':
            return _('You fired ({worker_name}).'.format(**data))

        if self.value == 'you_are_fired':
            return _('You are fired.')

        if self.value == 'you_has_new_worker':
            return _('You has a new worker. Wellcome {worker_name}.'.format(**data))


        raise NotImplementedError()
