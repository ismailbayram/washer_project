# from django.db.transaction import atomic
from cars.enums import CarType
from cars.models import Car


class CarService:
    # @atomic
    def create_car(self, license_plate, car_type, user):
        """
        :param license_plate: str
        :param car_type: CarType
        :param user: User
        :return: Car
        """
        car = Car.objects.create(licence_plate=license_plate,
                                 car_type=car_type,
                                 customer_profile=user.profile,
        )
        return car
