from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload_page, name='upload'),
    path('login', views.login_page, name='login'),
    path('register', views.register_page, name='register'),
    path('logout', views.logout_page, name='logout'),
    path('view/<str:filename>', views.return_file, name='view_file'),
    path('delete/<str:filename>', views.delete_page, name='delete')
]