from django.urls import path
from .views import *
from django.contrib import admin

urlpatterns = [
    path('', CreateMail, name='CreateMail'),
    path('download', DownloadFile, name='DownloadFile'),
    path('uploadmail', UploadMail, name='UploadMail'),
]