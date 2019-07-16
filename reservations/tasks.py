from washer_project.celery import app


@app.task(name="prevent_occupying_reservation")
def prevent_occupying_reservation(reservation_id):
    from reservations.models import Reservation
    from reservations.enums import ReservationStatus

    reservation = Reservation.objects.get(pk=reservation_id)
    if reservation.status == ReservationStatus.occupied:
        reservation.customer_profile = None
        reservation.status = ReservationStatus.available
        reservation.save()
