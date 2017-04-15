from django.shortcuts import render
from forms import Rasterform
from models import Rastermodel
from django.core.files.storage import FileSystemStorage
import os, sys

def submit(request):
    #if request.method == 'POST' and request.FILES['rasterR'] and request.FILES['rasterK'] and request.FILES['rasterLS'] and request.FILES['rasterC'] and request.FILES['rasterP']:
    if request.method == 'POST'  and request.FILES['rasterR'] and request.FILES['rasterK']:
        fileR = request.FILES['rasterR']
        fileK = request.FILES['rasterK']
        project = request.POST['project']
        fs = FileSystemStorage()
        filenameR = fs.save(project+"/"+fileR.name, fileR)
        filenameK = fs.save(project+'/'+fileK.name, fileK)
        uploaded_fileR_url = fs.url(filenameR)
        uploaded_fileK_url = fs.url(filenameK)


        form = Rasterform(request.POST, request.FILES)
        print(form.errors)
        if request.method == 'POST':
            if form.is_valid():
                print (fileR.name)
                form_success = 'form valid'
                form.save()
                os.system('gdalinfo '+fs.base_location+'\\'+ project + "\\" + fileR.name)
                os.system('gdalinfo '+fs.base_location+'\\'+ project + '\\' + fileK.name)
                #os.system('raster2pgsql -s Texas_South_Coordinate_System.proj4 '+ fs.base_location+ "\\" + project + "\\" + fileR.name + ' public.' + project + ' | psql -h localhost -p5432 -d Oso_Maintainer -U postgres')
                return render(request, '../templates/response.html', {
                    'uploaded_fileK_url': uploaded_fileR_url, 'uploaded_fileR_url': uploaded_fileK_url, 'form': form_success
                })

    return render(request, 'index.html')
