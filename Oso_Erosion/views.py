from django.shortcuts import render
from forms import Rasterform
from models import Rastermodel
from django.contrib.gis.gdal import GDALRaster
from django.core.files.storage import FileSystemStorage
import os, sys

osoMain = os.path.abspath(os.curdir)
osoErosion = osoMain+'\\Oso_Erosion\\'
def submit(request):
    # if request.method == 'POST' and request.FILES['rasterR'] and request.FILES['rasterK'] and request.FILES['rasterLS'] and request.FILES['rasterC'] and request.FILES['rasterP']:
    if request.method == 'POST' and request.FILES['rasterR'] and request.FILES['rasterK']:
        fileR = request.FILES['rasterR']
        fileK = request.FILES['rasterK']
        project = request.POST['project']
        fs = FileSystemStorage()
        filenameR = fs.save(project + "/" + fileR.name, fileR)
        filenameK = fs.save(project + '/' + fileK.name, fileK)
        rasterArray = []
        factorArray = [fileR.name, fileK.name]
        rasterR = GDALRaster(fs.base_location + '\\' + project + '\\' + fileR.name)
        rasterK = GDALRaster(fs.base_location + '\\' + project + '\\' + fileK.name)
        rasterArray.extend((rasterR, rasterK))

        coordSysRaster = []
        southTx83 = 32141
        for raster in rasterArray:
            coordSysRaster.append(raster.srs.srid)
            for coord in coordSysRaster:
                    if (coord != southTx83):
                        raster.transform(osoErosion + 'Texas_South_Coordinate_System.proj4')
                       

            form = Rasterform(request.POST, request.FILES)
            print(form.errors)
            if request.method == 'POST':
                if form.is_valid():
                    form_success = 'form valid'
                    # form.save()
                    # os.system('gdalinfo ' + fs.base_location + '\\' + project + "\\" + fileR.name)
                    # os.system('gdalinfo ' + fs.base_location + '\\' + project + '\\' + fileK.name)
                    # os.system('raster2pgsql -s Texas_South_Coordinate_System.proj4 '+ fs.base_location+ "\\" + project + "\\" + fileR.name + ' public.' + project + ' | psql -h localhost -p5432 -d Oso_Maintainer -U postgres')
                    # return render(request, '../templates/response.html', {
                    # 'uploaded_fileK_url': uploaded_fileR_url, 'uploaded_fileR_url': uploaded_fileK_url,
                    # 'form': form_success
                    # })

        return render(request, 'index.html')
