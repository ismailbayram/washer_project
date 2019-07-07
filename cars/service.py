from django.db.transaction import atomic
from django.db.utils import IntegrityError
import rest_framework.exceptions

from cars.enums import CarType
from cars.models import Car
from cars.exceptions import DublicateCarException

class CarService:
    # TODO: select created car
    def create_car(self, licence_plate, car_type, customer_profile):
        """
        :param license_plate: str
        :param car_type: CarType
        :param customer_profile: CustomerProfile
        :return: Car
        """
        car = Car.objects.create(
                    licence_plate=licence_plate,
                    car_type=car_type,
                    customer_profile=customer_profile,
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

    def deactivate_car(self, car):
        """
        :param car: Car
        """
        car.is_active = False
        car.is_selected = False
        car.save()
        return car

    def select_car(self, car, customer_profile):
        """
        :param car: Car
        :param customer_profile: CustomerProfile
        """

        Car.objects.filter(customer_profile=customer_profile).update(is_selected=False)

        car.is_selected = True
        car.save()
        return car
