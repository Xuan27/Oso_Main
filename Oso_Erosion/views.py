from django.shortcuts import render
from django.contrib.gis.gdal import GDALRaster, SpatialReference
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
import os, psycopg2


osoMain = os.path.abspath(os.curdir)
osoErosion = osoMain+'\\Oso_Erosion\\'
project = ''
factorArray = []

#Upload function that is triggered from the index/upload page
def upload(request):
    if request.method == 'POST' and request.FILES['rasterR'] and request.FILES['rasterK']:
        fileR = request.FILES['rasterR']
        fileK = request.FILES['rasterK']
        project = request.POST['project']
        R = request.POST['R']
        K = request.POST['K']
        factorArray = [R, K]
        try:
            conn = psycopg2.connect("dbname='Oso_Maintainer' user='postgres' host='localhost' password='lacucaracha'")
            cur = conn.cursor()
            print('Creating table')
            cur.execute("CREATE TABLE oso_projects." + project + " (rid BIGSERIAL PRIMARY KEY NOT NULL, rast RASTER, filename VARCHAR(200), rastfullpath VARCHAR(250), factor VARCHAR(10))")
            cur.close()
            conn.commit()
            conn.close()


        except psycopg2.Error as e:
            print(e.pgerror)
            print ("CREATE TABLE oso_projects." + project + "(rid BIGSERIAL PRIMARY KEY NOT NULL, rast RASTER, filename VARCHAR(200), rastfullpath VARCHAR(250), factor VARCHAR(10))")
            return render(request, '../templates/response.html', {
                'form': 'Rasters uploaded unsuccessfully: Unable to connect to the database.'
            })

        fs = FileSystemStorage()
        filenameR = fs.save(project + "/" + fileR.name, fileR)
        filenameK = fs.save(project + '/' + fileK.name, fileK)
        uploaded_fileR_url = fs.url(filenameR)
        uploaded_fileK_url = fs.url(filenameK)
        rasterArray = []

        rasterR = GDALRaster(fs.base_location + '\\' + project + '\\' + fileR.name)
        rasterK = GDALRaster(fs.base_location + '\\' + project + '\\' + fileK.name)
        rasterArray.extend((rasterR, rasterK))

        coordSysRaster = []
        wgs84 = 4326
        for element in range(0,2):
            print(rasterArray[element].srs.srid)
            print('Transforming Rasters')
            coordSysRaster.append(rasterArray[element].srs.srid)
            if coordSysRaster[element] != wgs84:
                rasterTransform = rasterArray[element].transform('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs ', driver='tiff')
                rasterArray.remove(rasterArray[element])
                rasterArray.append(rasterTransform)

        # isFactor = -1
        # arrFactor = []
        # arrRaster = []
        # find = rasterArray[0].name.rfind(factorArray[1], 0, 6)
        # print(find)
        # count = 0
        # while (isFactor == -1):
        #     print (isFactor)
        #     for element in range(0, 2):
        #         print(element)
        #         isFactor = rasterArray[element].name.rfind(factorArray[count], 0, 6)
        #         if (isFactor != -1):
        #             arrFactor.append(rasterArray[element])
        #             arrRaster.append(factorArray[count])
        #             print(arrFactor)
        #             print(arrRaster)
        #         count += 1




        x = os.system('raster2pgsql -a -I -C -M -F -s 4326 ' + rasterArray[0].name + ' ' + rasterArray[1].name + ' oso_projects' + '.' + project + ' | psql -h localhost -p5432 -d Oso_Maintainer -U postgres')

        try:
            conn = psycopg2.connect("dbname='Oso_Maintainer' user='postgres' host='localhost' password='lacucaracha'")
            cur = conn.cursor()
            for element in range(0, 2):
                print (element)
                print("UPDATE oso_projects.%s SET rastfullpath = '%s' WHERE rid = %s;" %(project, rasterArray[element].name, element))
                cur.execute("UPDATE oso_projects.%s SET rastfullpath = '%s', factor = '%s' WHERE rid = %s;" %(project, rasterArray[element].name, factorArray[element], element+1))
            conn.commit()
            conn.close()

        except psycopg2.Error as e:
            print(e.pgerror)
            return render(request, '../templates/response.html', {
                'form': 'Rasters uploaded unsuccessfully: Unable to connect to the database and store raster full path.'
            })

        if (x == 0):

            return render(request, '../templates/response.html', {
                'uploaded_fileK_url': uploaded_fileK_url, 'uploaded_fileR_url': uploaded_fileR_url,
                'form': 'Rasters uploaded successfully', 'schema': project, 'factors': factorArray
             })
    if request.method == 'GET' and 'abstraction' in request.GET:
        abstraction = request.GET['abstraction']
        if abstraction is not None and abstraction != '':
            project = request.GET['project']
            factorsTables = []

            try:
                connect = psycopg2.connect("dbname='Oso_Maintainer' user='postgres' host='localhost' password='lacucaracha'")
                cur = connect.cursor()
                cur.execute("SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema = '%s'" %(project))
                tables = [r[0] for r in cur.fetchall()]
                for table in tables:
                    factorsTables.append(table)
                for table in factorsTables:
                    # cur.execute('SELECT rastfullpath FROM %s.%s WHERE rid=1'%(project,table))
                    cur.execute("SELECT ST_AsGDALRaster(%s.rast, 'PNG') AS rastpng FROM %s.%s WHERE rid=1" %(table,project,table))
                rastPath = [r[0] for r in cur.fetchall()]

                cur.close()
                connect.commit()
                connect.close()
                # print('rasterpath')
                print(rastPath)
                # print('gdal2tiles -p raster -s 4326 -z 10 -w none -e %s ../Tiles/%s'%(rastPath[0], project))
                # os.system('gdal2tiles -p mercator -s 3857 -z 0-10 -w none -e %s Raster/Tiles/%s'%(rastPath[0], project))
            except psycopg2.Error as e:
                print(e.pgerror)

            return redirect('/upload/response/')


    #if request.method == 'GET' and request.GET['abstraction']:
    # try:
    #     abstraction = request.GET['abstraction']
    #     abstraction = True

        # connect = psycopg2.connect("dbname='Oso_Maintainer' user='postgres' host='localhost' password='lacucaracha'")
        # cur = connect.cursor()
        # cur.execute("SET search_path TO " + project + ";")
        # for factor in factorArray:
        #     cur.execute("SELECT ST_FromGDALRaster(png) AS rast FROM " + factor)
        # print ('fetching')
        # print (cur.fetchall())
        # cur.close()
        # connect.commit()
        # connect.close()
    # except KeyError:
    #     print('not in abstraction')

        # if(request.GET['abstraction'] == 'Create Erosion Map'):
        #     print('im in the returned request')
        # print('probably working')
        # try:
        #     conn = psycopg2.connect("dbname='Oso_Maintainer' user='postgres' host='localhost' password='lacucaracha'")
        #     cur = conn.cursor()
        #     cur.execute("SET search_path TO " + project + ";")
        #     for factor in factorArray:
        #         cur.execute("SELECT ST_FromGDALRaster(png) AS rast FROM " + factor)
        #     print ('fetching')
        #     print (cur.fetchall())
        #     cur.close()
        #     conn.commit()
        #     conn.close()
        #
        # except psycopg2.Error as e:
        #     print(e.pgerror)

        #return render(request, '../templates/response.html')
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
                    #

    return render(request, 'index.html')

def map(request):
    if request.method == 'GET':
        try:
            conn = psycopg2.connect("dbname='Oso_Maintainer' user='postgres' host='localhost' password='lacucaracha'")
            cur = conn.cursor()
            # selection = cur.execute("SELECT TABLE_NAME FROM information_schema.tables;")
            # print (cur.fetchall())
            cur.close()
            conn.commit()
            conn.close()

        except psycopg2.Error as e:
            print(e.pgerror)
            #print ("I am unable to connect to the database.")
    # result = os.system("echo \dn | psql -h localhost -p5432 -d Oso_Maintainer -U postgres")
    # print (result)
    return render(request, '../templates/map.html')
    # if request.method == 'POST':
    #     print (result)
