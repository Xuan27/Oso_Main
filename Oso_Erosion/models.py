from __future__ import unicode_literals
from django.db import models

#Rasterfile information table with the raster column
class Rastermodel(models.Model):
    project = models.CharField(max_length=80)
    rasterpath = models.ImageField(upload_to='Projects/', null=True, blank=True)

    def __str__(self):
        return self.name

