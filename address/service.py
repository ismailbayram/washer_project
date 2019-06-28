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
    # TODO: AddressService test
    def create_address(self, country, city, township, line, postcode=None):
        """
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

        return address

    def update_address(self, instance, country, city, township,
                       line, postcode=None):
        """
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

        instance.country = country
        instance.city = city
        instance.township = township
        instance.line = line
        instance.postcode = postcode

        return instance
