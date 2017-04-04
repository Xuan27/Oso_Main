import os
from django.contrib.gis.utils import LayerMapping
from raster.models import Legend, LegendEntry, LegendEntryOrder, LegendSemantics
from django.contrib.gis.gdal import GDALRaster


raster = 'C:\Users\Juan\Documents\GIS Projects\Oso_Maintainer\Data\CitySup_USGS.tif'
rst_obj = GDALRaster(raster, write=False)
