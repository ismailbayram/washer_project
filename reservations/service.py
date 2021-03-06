import datetime

import pytz
from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.transaction import atomic
from django.utils.crypto import get_random_string

from baskets.exceptions import BasketEmptyException
from baskets.service import BasketService
from notifications.enums import NotificationType
from notifications.service import NotificationService
from reservations.enums import ReservationStatus
from reservations.exceptions import (ReservationAlreadyCommented,
                                     ReservationAlreadyReplyed,
                                     ReservationCanNotCancelledException,
                                     ReservationCompletedException,
                                     ReservationExpiredException,
                                     ReservationHasNoComment,
                                     ReservationIsNotComplated,
                                     ReservationNotAvailableException,
                                     ReservationOccupiedBySomeoneException,
                                     ReservationStartedException, ReservationAlreadyExist)
from reservations.models import Comment, Reservation
from reservations.tasks import (prevent_occupying_reservation,
                                send_reminder_reservation_notification)
from stores.exceptions import StoreNotAvailableException


class ReservationService(object):
    def _generate_reservation_number(self):
        number = get_random_string(length=10).upper()
        if Reservation.objects.filter(number=number).exists():
            return self._generate_reservation_number()
        return number

    def _create_reservation(self, store, start_datetime, period):
        """
        :param store: Store
        :param start_datetime: DateTime
        :param period: int
        :return: Reservation
        """
        try:
            reservation = Reservation.objects.get(store=store, start_datetime=start_datetime)
        except Reservation.DoesNotExist:
            end_datetime = start_datetime + datetime.timedelta(minutes=period)
            reservation = Reservation.objects.create(store=store, start_datetime=start_datetime,
                                                     end_datetime=end_datetime, period=period,
                                                     number=self._generate_reservation_number())
        return reservation

    def create_day_from_config(self, store, day_datetime, period):
        """
        :param store: Store
        :param day_datetime: DateTime
        :param period: int
        :return: list
        """
        timezone = pytz.timezone(settings.TIME_ZONE)
        config = store.config['reservation_hours']
        day = day_datetime.strftime("%A").lower()

        start = config[day]['start']
        end = config[day]['end']
        if start is None:
            return []

        start_time = datetime.datetime.strptime(start, "%H:%M")
        end_time = datetime.datetime.strptime(end, "%H:%M")
        diff = (end_time - start_time).seconds / 60
        period_count = int(diff / period)

        start_datetime = day_datetime.replace(hour=start_time.hour, minute=start_time.minute,
                                              second=0, microsecond=0)
        res_pk_list = []
        for p in range(period_count):
            start_dt = start_datetime + datetime.timedelta(minutes=(p * period))
            start_dt = timezone.localize(start_dt)
            reservation = self._create_reservation(store=store, start_datetime=start_dt, period=period)
            res_pk_list.append(reservation.pk)
        return res_pk_list

    @atomic
    def create_week_from_config(self, store):
        """
        :param store: Store
        :return: set
        """
        period = store.product_set.filter(is_primary=True).order_by('-period').first().period

        res_pk_list = []
        for k in range(1, 8):
            day_datetime = datetime.datetime.today() + datetime.timedelta(days=k)
            pk_list = self.create_day_from_config(store, day_datetime, period)
            res_pk_list += pk_list
        return set(res_pk_list)

    def occupy(self, reservation, customer_profile):
        """
        :param reservation: Reservation
        :param customer_profile: CustomerProfile
        :return: Reservation
        """
        try:
            occupied = customer_profile.reservation_set.get(status=ReservationStatus.occupied)
            occupied.status = ReservationStatus.available
            occupied.customer_profile = None
            occupied.save(update_fields=['status', 'customer_profile'])
        except Reservation.DoesNotExist:
            pass

        if reservation.status > ReservationStatus.occupied:
            raise ReservationNotAvailableException
        if reservation.status == ReservationStatus.occupied:
            if not reservation.customer_profile == customer_profile:
                raise ReservationOccupiedBySomeoneException
            return reservation
        if not (reservation.store.is_active and reservation.store.is_approved):
            raise StoreNotAvailableException

        reservation_exist = customer_profile.reservation_set.filter(
            start_datetime__gte=reservation.start_datetime - datetime.timedelta(hours=1),
            end_datetime__lte=reservation.end_datetime + datetime.timedelta(hours=1)
        )
        if reservation_exist:
            raise ReservationAlreadyExist
        timezone = pytz.timezone(settings.TIME_ZONE)
        dt = reservation.start_datetime
        now = timezone.localize(datetime.datetime.now())
        if dt < now:
            raise ReservationExpiredException

        occupy_timeout = 60 * 4
        prevent_occupying_reservation.apply_async((reservation.pk, ), countdown=occupy_timeout)
        reservation.status = ReservationStatus.occupied
        reservation.customer_profile = customer_profile
        reservation.save(update_fields=['status', 'customer_profile'])

        return reservation

    def reserve(self, reservation, customer_profile):
        """
        :param reservation: Reservation
        :param customer_profile: CustomerProfile
        :return: Reservation
        """
        if reservation.status > ReservationStatus.occupied:
            raise ReservationNotAvailableException
        if reservation.customer_profile is not None and \
                not customer_profile == reservation.customer_profile:
            raise ReservationOccupiedBySomeoneException

        basket_service = BasketService()
        basket = basket_service.get_or_create_basket(customer_profile)

        if basket.is_empty:
            raise BasketEmptyException

        if not basket.basketitem_set.first().product.store == reservation.store:
            basket = basket_service.clean_basket(basket)

        with atomic():
            basket = basket_service.complete_basket(basket)

            reservation.basket = basket
            reservation.total_amount = basket.get_total_amount()
            reservation.net_amount = basket.get_net_amount()
            reservation.status = ReservationStatus.reserved
            reservation.save()

            notif_service = NotificationService()
            notif_service.send(instance=reservation, to=reservation.store,
                               notif_type=NotificationType.reservation_reserved,)
            notif_service.send(instance=reservation, to=customer_profile,
                               notif_type=NotificationType.reservation_reserved,)

            reminder_dt = reservation.start_datetime - datetime.timedelta(minutes=30)
            send_reminder_reservation_notification.apply_async((customer_profile.pk,
                                                                reservation.pk),
                                                               eta=reminder_dt)

        return reservation

    def start(self, reservation):
        """
        :param reservation: Reservation
        :return: reservation
        """
        if reservation.status < ReservationStatus.reserved:
            raise ReservationNotAvailableException
        if reservation.status > ReservationStatus.reserved:
            raise ReservationStartedException
        reservation.status = ReservationStatus.started
        reservation.save(update_fields=['status'])

        notif_service = NotificationService()
        notif_service.send(instance=reservation, to=reservation.store,
                           notif_type=NotificationType.reservation_started,)
        notif_service.send(instance=reservation, to=reservation.customer_profile,
                           notif_type=NotificationType.reservation_started)

        return reservation

    def complete(self, reservation):
        """
        :param reservation: Reservation
        :return: reservation
        """
        if reservation.status < ReservationStatus.started:
            raise ReservationNotAvailableException
        if reservation.status > ReservationStatus.started:
            raise ReservationCompletedException
        reservation.status = ReservationStatus.completed
        reservation.save(update_fields=['status'])

        notif_service = NotificationService()
        notif_service.send(instance=reservation, to=reservation.store,
                           notif_type=NotificationType.reservation_completed)
        notif_service.send(instance=reservation, to=reservation.customer_profile,
                           notif_type=NotificationType.reservation_completed)

        return reservation

    def cancel(self, reservation, cancellation_reason):
        """
        :param reservation: Reservation
        :param cancelation_reason: CancellationReason
        :return: reservation
        """
        if not reservation.status == ReservationStatus.reserved:
            raise ReservationCanNotCancelledException
        reservation.status = ReservationStatus.cancelled
        reservation.cancellation_reason = cancellation_reason
        reservation.save(update_fields=['status', 'cancellation_reason'])

        notif_service = NotificationService()
        notif_service.send(instance=reservation, to=reservation.store,
                           notif_type=NotificationType.reservation_cancelled)
        notif_service.send(instance=reservation, to=reservation.customer_profile,
                           notif_type=NotificationType.reservation_cancelled)
        return reservation

    def disable(self, reservation):
        """
        :param reservation: Reservation
        :return: reservation
        """
        if not reservation.status == ReservationStatus.available:
            raise ReservationNotAvailableException

        notif_service = NotificationService()
        notif_service.send(instance=reservation, to=reservation.store,
                           notif_type=NotificationType.reservation_disabled)


        reservation.status = ReservationStatus.disabled
        reservation.save(update_fields=['status'])
        return reservation

    def expire(self, reservation):
        """
        :param reservation: Reservation
        :return: reservation
        """

        notif_service = NotificationService()
        notif_service.send(instance=reservation, to=reservation.store,
                           notif_type=NotificationType.reservation_expired)

        reservation.status = ReservationStatus.expired
        reservation.save(update_fields=['status'])
        return reservation


class CommentService:
    def _update_store_rating(self, store, new_rating):
        """
        :param store: Store
        :param new_rating: Int
        """
        q = Comment.objects.filter(reservation__store=store)
        total_rating = q.aggregate(score=Coalesce(Sum('rating'),0)).get('score')
        total_count = q.count()
        store.rating = (total_rating + new_rating) / float(total_count + 1)
        store.save(update_fields=['rating'])

    @atomic
    def comment(self, rating, comment, reservation):
        """
        :param rating: Int
        :param comment: String
        :param reservation: Reservation
        :return: Reservation
        """
        if reservation.status != ReservationStatus.completed:
            raise ReservationIsNotComplated

        try:
            _ = reservation.comment
            raise ReservationAlreadyCommented
        except Reservation.comment.RelatedObjectDoesNotExist:
            pass

        self._update_store_rating(store=reservation.store, new_rating=rating)
        comment = Comment.objects.create(rating=rating, comment=comment,
                                         reservation=reservation)
        return comment


    def reply(self, reply, reservation):
        """
        :param reply: String
        :param reservation: Reservation
        :return: Reservation
        """
        try:
            comment = reservation.comment
        except Reservation.comment.RelatedObjectDoesNotExist:
            raise ReservationHasNoComment

        if comment.reply:
            raise ReservationAlreadyReplyed

        comment.reply = reply
        comment.save(update_fields=['reply'])
        return comment
