from django.db.transaction import atomic

from address.models import Address
from address.exceptions import CityNotValidException, TownshipNotValidException


class CountryService:
    def deactive_country(self, country):
        country.is_active = False
        country.save()
        return country


class CityService:
    def deactive_city(self, city):
        city.is_active = False
        city.save()
        return city


class TownshipService:
    def deactive_township(self, township):
        township.is_active = False
        township.save()
        return township


class AddressService:
    @atomic
    def create_address(self, store, country, city, township, line, postcode=None):
        """
        :param store: Store
        :param country: Country
        :param city: City
        :param township: Township
        :param postcode: str
        :param line: str
        :return: Address
        """
        if not city.country == country:
            raise CityNotValidException(params=(city, country))

        if not township.city == city:
            raise TownshipNotValidException(params=(township, city))

        address = Address.objects.create(country=country, city=city,
                                         township=township, line=line,
                                         postcode=postcode)

        if store.address:
            store.address.delete()

        store.address = address
        store.is_approved = False
        store.save(update_fields=['address', 'is_approved'])

        return address
