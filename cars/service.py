# from django.db.transaction import atomic
import rest_framework.exceptions

from cars.enums import CarType
from cars.models import Car


class CarService:
    # @atomic
    def create_car(self, licence_plate, car_type, user):
        """
        :param license_plate: str
        :param car_type: CarType
        :param user: User
        :return: Car
        """
        car = Car.objects.create(
            licence_plate=licence_plate,
            car_type=car_type,
            customer_profile=user.customer_profile,
        )
        return car

    def update_car(self, car, licence_plate=None, car_type=None, user=None, **kwargs):
        """
        :param car: Car
        :param license_plate: str
        :param car_type: CarType
        :param user: User
        :return: Car
        """
        if user.customer_profile != car.customer_profile:
            # TODO bu permission buraya olmadı
            raise rest_framework.exceptions.PermissionDenied

        if licence_plate:
            car.licence_plate = licence_plate
        if car_type:
            car.car_type = car_type

        car.save()
        return car
