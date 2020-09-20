import os
from mimetypes import guess_type

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.encoding import smart_str
from django.http import HttpResponse
from django.contrib.auth.models import User

import humanize

from .models import File

FILE_DIR = 'files/'

def index(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    return render(request, 'index.html', {'username': request.user.get_username(), 'staff': request.user.is_superuser, 'files': File.objects.all()})

def __handle_file_upload(request, file):
    with open(FILE_DIR + file.name, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    new_file = File(uploader=request.user.get_username(), filename=file.name, path=FILE_DIR + file.name, size=humanize.naturalsize(file.size))
    new_file.save()

def upload_page(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    if not request.FILES:
        return redirect('/')
    
    for file in request.FILES.getlist('file-input'):
        __handle_file_upload(request, file)

    return redirect('/')

def download_page(request, filename):
    if not request.user.is_authenticated:
        return redirect('/login')
    
    if File.objects.get(filename=filename) is None:
        return redirect('/')

    filepath = smart_str(File.objects.get(filename=filename).path)
    with open(filepath, 'rb') as file:
        response = HttpResponse(file, content_type=guess_type(filepath)[0])
        response['Content-Length'] = len(response.content)
        return response

def delete_page(request, filename):
    if not request.user.is_authenticated:
        return redirect('/login')
    
    if File.objects.get(filename=filename) is None or (File.objects.get(filename=filename).uploader != request.user.get_username() and not request.user.is_superuser):
        return redirect('/')

    os.remove(os.path.join(FILE_DIR, filename))
    File.objects.get(filename=filename).delete()

    return redirect('/')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('/')
    
    return render(request, 'login.html')

def register_page(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        if User.objects.filter(username=request.POST['username']).exists() or User.objects.filter(email=request.POST['email']).exists():
            return redirect('/register' + '?taken=1')

        user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
        user.is_active = False
        user.save()
        return redirect('/login')

    return render(request, 'register.html')

def logout_page(request):
    logout(request)
    return redirect('/')