from django.shortcuts import render
from forms import Rasterform
from models import Rastermodel
from django.core.files.storage import FileSystemStorage
import os

def submit(request):
    if request.method == 'POST' and request.FILES['raster']:
        file = request.FILES['raster']
        project = request.POST['project']
        print(project)
        fs = FileSystemStorage()
        filename = fs.save(project+file.name, file)
        uploaded_file_url = fs.url(filename)
        print(fs.base_location)
        print(file.name)
        os.system()

        form = Rasterform(request.POST, request.FILES)
        print(form.errors)
        if request.method == 'POST':
            if form.is_valid():
                print (form['rasterpath'])
                form_success = 'form valid'
                form.save()
                return render(request, '../templates/response.html', {
                    'uploaded_file_url': uploaded_file_url, 'form': form_success
                })

            else:
                form = Rasterform()
                print('Errors')
                form_error = 'form is still not valid'
                return render(request, '../templates/response.html', {
                    'uploaded_file_url': uploaded_file_url, 'form': form_error
                })

    return render(request, 'index.html')
