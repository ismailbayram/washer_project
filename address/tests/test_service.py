from django.test import TestCase
from model_mommy import mommy

from address.exceptions import CityNotValidException, TownshipNotValidException
from address.models import Address
from address.service import AddressService


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
        self.store = mommy.make('stores.Store', is_approved=True)


class AddressServiceTest(BaseLocationTestCase):
    service = AddressService()

    def test_create_address(self):
        data = {
            'store': self.store,
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
        self.store.refresh_from_db()
        self.assertIsNotNone(self.store.address)
        self.assertEqual(self.store.is_approved, False)
        self.assertEqual(address.country, data['country'])
        self.assertEqual(address.city, data['city'])
        self.assertEqual(address.township, data['township'])
        self.assertEqual(address.line, data['line'])
        self.assertEqual(address.postcode, data['postcode'])

    def test_update_address(self):
        data = {
            'store': self.store,
            'country': self.country,
            'city': self.city,
            'township': self.township,
            'line': 'Arka Sokak, Nu:1',
            'postcode': '34220'
        }
        address = self.service.create_address(**data)
        self.assertIsNotNone(self.store.address)
        self.assertEqual(Address.objects.filter(pk=address.pk).count(), 1)
        self.assertEqual(self.store.is_approved, False)

        address2 = self.service.create_address(**data)
        self.assertIsNotNone(self.store.address)
        self.assertEqual(self.store.is_approved, False)
        self.assertEqual(Address.objects.filter(pk=address.pk).count(), 0)
        self.assertEqual(Address.objects.filter(pk=address2.pk).count(), 1)
