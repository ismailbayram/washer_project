from django.db.transaction import atomic
import rest_framework.exceptions

from cars.enums import CarType
from cars.models import Car


class CarService:
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

    def update_car(self, car, licence_plate=None, car_type=None,  **kwargs):
        """
        :param car: Car
        :param license_plate: str
        :param car_type: CarType
        :return: Car
        """
        if licence_plate:
            car.licence_plate = licence_plate
        if car_type:
            car.car_type = car_type

        car.save()
        return car

    def disable_car(self, car):
        """
        :param car: Car
        """
        car.is_active = False
        car.save()
        return car

    @atomic
    def select_car(self, car, user):
        """
        :param car: Car
        :param user: User
        """

        Car.objects.filter(customer_profile = user.customer_profile).update(is_selected=False)

        car.is_selected = True
        car.save()
        return car
