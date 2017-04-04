from __future__ import unicode_literals

from django.contrib.gis.db import models

class ElevationRaster(models.Model):
    storage_name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50)


# Create your models here.
