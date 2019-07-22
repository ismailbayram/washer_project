from django.core.paginator import Paginator, Page


class ESPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._count = self.object_list.hits.total

    def page(self, number):
        number = self.validate_number(number)
        return Page(self.object_list, number, self)
