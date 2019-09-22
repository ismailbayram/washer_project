import datetime
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone

from admin.dashboard.enums import GroupTimeType
from stores.models import Store


class DashboardService:
    @staticmethod
    def get_stores_waiting_approve():
        return Store.objects.filter(is_approved=False).order_by('modified_date')[:5]

    @staticmethod
    def _get_next_date(date, group_time):
        if group_time == GroupTimeType.month:
            # last day of last month
            re = datetime.datetime(
                year=date.year if date.month+1 < 13 else date.year+1,
                month=date.month+1 if date.month+1 < 13 else 1,
                day=1
            )
            re = timezone.make_aware(re, timezone.get_default_timezone())
            return re

        elif group_time == GroupTimeType.day:
            return date + datetime.timedelta(days=1)

        elif group_time == GroupTimeType.hour:
            return date + datetime.timedelta(hours=1)

    def grouping_with_time(self, function, queryset, lookup_field, group_time,
                           start_date, end_date, *args, **kwargs):
        """
        :param function: Function
        :parm queryset: QuerySet
        :param lookup_field: String (grouping time field name on the db)
        :param group_time: GroupTimeType
        :return: Dictinoary

        This function do:
        1) N time:
          1) filter the queryset with time
          2) pass the new queryset to function
          3) assign returned value on setep 2 to return_dict[time]
        2) return return_dict
        """
        result = {}

        time_strings = {
            GroupTimeType.hour: "%H:%M",
            GroupTimeType.month: "%d-%m-%Y",
            GroupTimeType.day:  "%d-%m-%Y",
        }

        while start_date < end_date:
            next_date = self._get_next_date(start_date, group_time)
            f_queryset = queryset.filter(
                **{lookup_field+"__range": [start_date, next_date]}
            )
            func_result = function(f_queryset, *args, **kwargs)
            result[start_date.strftime(time_strings[group_time])] = func_result
            start_date = next_date

        return result

    @staticmethod
    def get_total_users_on_grups_count(queryset):
        """
        :param queryset: QuerySet<User>
        :param group_time: GroupTimeType
        "example return:
        {
          "customer": 10,
          "washer": 20,
          "worker": 40
        }
        """
        groups = (
            queryset.all()
            .values("groups__name")
            .annotate(count=Count("groups"))
        )
        return_dict = {
            "customer": 0,
            "washer": 0,
            "worker": 0,
        }
        for group in groups:
            return_dict[group['groups__name']] = group['count']
        return return_dict

    @staticmethod
    def get_total_store_count(queryset):
        return queryset.count()

    @staticmethod
    def get_total_reservation_and_profit(queryset):
        """
        :param queryset: QuerySet
        :return: dict
        """
        endorsement = (
            queryset
            .aggregate(total=Sum("net_amount"))
        ).get('total')

        if not endorsement:
            endorsement = 0
        endorsement = Decimal(endorsement)

        total_reservation = queryset.count()

        return {
            "endorsement": endorsement,
            "profit": endorsement * Decimal(0.15),
            "total_reservations": total_reservation,
        }
