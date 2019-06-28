from django.db import models

from base.models import StarterModel


class AbstractLocation(StarterModel):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Country(AbstractLocation):
    code = models.CharField(max_length=3, unique=True)


class City(AbstractLocation):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('country', 'name')


class Township(AbstractLocation):
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('city', 'name')


class Address(StarterModel):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    township = models.ForeignKey(Township, on_delete=models.SET_NULL, null=True)
    postcode = models.CharField(max_length=24, null=True, blank=True)
    line = models.CharField(max_length=256)
