from model_mommy import mommy
from django.test import TestCase

from address.service import AddressService
from address.exceptions import TownshipNotValidException, CityNotValidException


class BaseLocationTestCase(TestCase):
    def setUp(self):
        self.country = mommy.make('address.Country', name="turkey")
        self.country2 = mommy.make('address.Country', name="valhalla")
        self.city = mommy.make('address.City', name="istanbul", country=self.country)
        self.city2 = mommy.make('address.City', name="ragnar", country=self.country2)
        self.township = mommy.make('address.Township', name="sisli", city=self.city)
        self.township2 = mommy.make('address.Township', name="valhalla merkez", city=self.city2)
        self.address = mommy.make('address.Address', country=self.country, city=self.city,
                                  township=self.township)


class AddressServiceTest(BaseLocationTestCase):
    service = AddressService()

    def test_create_address(self):
        data = {
            'country': self.country,
            'city': self.city2,
            'township': self.township2,
            'line': 'Arka Sokak, Nu:1',
            'postcode': '34220'
        }

        with self.assertRaises(CityNotValidException):
            self.service.create_address(**data)

        data.update({'city': self.city})

        with self.assertRaises(TownshipNotValidException):
            self.service.create_address(**data)

        data.update({'township': self.township})
        address = self.service.create_address(**data)
        self.assertEqual(address.country, data['country'])
        self.assertEqual(address.city, data['city'])
        self.assertEqual(address.township, data['township'])
        self.assertEqual(address.line, data['line'])
        self.assertEqual(address.postcode, data['postcode'])

    def test_update_address(self):
        data = {
            'country': self.country2,
            'city': self.city,
            'township': self.township,
            'line': 'Arka Sokak, Nu:1',
            'postcode': '34220'
        }

        with self.assertRaises(CityNotValidException):
            self.service.update_address(self.address, **data)

        data.update({'city': self.city2})

        with self.assertRaises(TownshipNotValidException):
            self.service.update_address(self.address, **data)

        data.update({'township': self.township2})
        self.service.update_address(self.address, data)
        self.address.refresh_from_db()
        self.assertEqual(self.address.country, data['country'])
        self.assertEqual(self.address.city, data['city'])
        self.assertEqual(self.address.township, data['township'])
        self.assertEqual(self.address.line, data['line'])
        self.assertEqual(self.address.postcode, data['postcode'])
