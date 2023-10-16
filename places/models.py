from django.db import models
from django.utils import timezone


class Place(models.Model):
    geocode_date = models.DateField('Дата запроса', default=timezone.now)
    address = models.CharField('Адрес', max_length=255)
    lat = models.DecimalField('Широта', max_digits=9, decimal_places=6)
    lon = models.DecimalField('Долгота', max_digits=9, decimal_places=6)

    class Meta:
        unique_together = ['lat', 'lon', 'address']

    def __str__(self):
        return self.address
