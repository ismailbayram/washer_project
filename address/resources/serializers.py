from rest_framework import serializers

from address.models import Country, City, Township, Address


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('pk', 'name', )


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('pk', 'name', 'country')


class TownshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Township
        fields = ('pk', 'name', 'city')


class AddressSerializer(serializers.ModelSerializer):
    # TODO: validate city and township here
    class Meta:
        model = Address
        fields = ('pk', 'country', 'city', 'township', 'line', 'postcode',)


class AddressDetailedSerializer(AddressSerializer):
    country = CountrySerializer()
    city = CitySerializer()
    township = TownshipSerializer()
    line = serializers.CharField(min_length=10)

    class Meta(AddressSerializer.Meta):
        pass
