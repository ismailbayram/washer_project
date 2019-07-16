from washer_project.celery import app


@app.task(name="reservations.prevent_occupying_reservation")
def prevent_occupying_reservation(reservation_id):
    from reservations.models import Reservation
    from reservations.enums import ReservationStatus

    reservation = Reservation.objects.get(pk=reservation_id)
    if reservation.status == ReservationStatus.occupied:
        reservation.customer_profile = None
        reservation.status = ReservationStatus.available
        reservation.save()


@app.task(name="reservations.create_store_weekly_reservations")
def create_store_weekly_reservations(store_id):
    from stores.models import Store
    from reservations.service import ReservationService

    res_service = ReservationService()
    store = Store.objects.get(pk=store_id)
    res_service.create_week_from_config(store)
    # NOTIFICATION

# TODO: periodic task for the day that is after 7 days from now
