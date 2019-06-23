

class CountryService():
    def deactive_country(self, country):
        country.is_active = False
        country.save()
        return country


class CityService():
    def deactive_city(self, city):
        city.is_active = False
        city.save()
        return city


class TownshipService():
    def deactive_township(self, township):
        township.is_active = False
        township.save()
        return township

