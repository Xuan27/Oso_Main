from django.shortcuts import render
from django.contrib.gis.gdal import GDALRaster
from django.core.files.storage import FileSystemStorage
import os, psycopg2


osoMain = os.path.abspath(os.curdir)
osoErosion = osoMain+'\\Oso_Erosion\\'

def submit(request):
    if request.method == 'POST' and request.FILES['rasterR'] and request.FILES['rasterK']:
        fileR = request.FILES['rasterR']
        fileK = request.FILES['rasterK']
        project = request.POST['project']
        R = request.POST['R']
        K = request.POST['K']
        factorArray = [R, K]
        try:
            conn = psycopg2.connect("dbname='Oso_Maintainer' user='postgres' host='localhost' password='lacucaracha'")

        except:
            print ("I am unable to connect to the database.")

        cur = conn.cursor()
        cur.execute("CREATE SCHEMA " + project + ";")
        for factor in factorArray:
            cur.execute("CREATE TABLE " + project + "." + factor + "(rid BIGSERIAL PRIMARY KEY NOT NULL, rast RASTER, filename VARCHAR(200))")
        cur.close()
        conn.commit()
        conn.close()

        fs = FileSystemStorage()
        filenameR = fs.save(project + "/" + fileR.name, fileR)
        filenameK = fs.save(project + '/' + fileK.name, fileK)
        rasterArray = []

        rasterR = GDALRaster(fs.base_location + '\\' + project + '\\' + fileR.name)
        rasterK = GDALRaster(fs.base_location + '\\' + project + '\\' + fileK.name)
        rasterArray.extend((rasterR, rasterK))

        coordSysRaster = []
        southTx83 = 32141
        for raster in rasterArray:
            coordSysRaster.append(raster.srs.srid)
            for coord in coordSysRaster:
                    if (coord != southTx83):
                        rasterTransform = raster.transform(osoErosion + 'Texas_South_Coordinate_System.proj4', driver='tiff')
                        rasterArray.remove(raster)
                        rasterArray.append(rasterTransform)
        for element in range(0,2):
            print(rasterArray[element].name)
            os.system('raster2pgsql -s Texas_South_Coordinate_System.proj4 -F -M -a ' + rasterArray[element].name + ' ' + project + '.' + factorArray[element] + ' | psql -h localhost -p5432 -d Oso_Maintainer -U postgres')

        #os.system('psql -h localhost -p5432 -d Oso_Maintainer -U postgres')
        #os.system('')
        #for raster in rasterArray:
            #os.system('gdalinfo ' + raster.name)


            #os.system('raster2pgsql -s Texas_South_Coordinate_System.proj4 -F -M -a '+ raster.name + ' public.test | psql -h localhost -p5432 -d Oso_Maintainer -U postgres')
        #form = Rasterform(request.POST, request.FILES)
        #print(form.errors)
        #if request.method == 'POST':
         #   if form.is_valid():
                    #form_success = 'form valid'
                    # form.save()
                    #
                    # os.system('raster2pgsql -s Texas_South_Coordinate_System.proj4 '+ fs.base_location+ "\\" + project + "\\" + fileR.name + ' public.' + project + ' | psql -h localhost -p5432 -d Oso_Maintainer -U postgres')
                    # return render(request, '../templates/response.html', {
                    # 'uploaded_fileK_url': uploaded_fileR_url, 'uploaded_fileR_url': uploaded_fileK_url,
                    # 'form': form_success
                    # })

    return render(request, 'index.html')
