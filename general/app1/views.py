import base64
from io import *


from django.http import *
import time
from django.shortcuts import * # для отображения шаблонов
from django.views.generic import *
from .forms import *
from app1.models import *
from app1.CheckMails import *
import os
import datetime
import re
from django.core.files.base import ContentFile
import matplotlib.pyplot as plt
import pandas as pd
import plotly
from urllib.parse import urlparse
import csv
from django.contrib import messages
from .uploading import *
import openpyxl

def UploadMail(request):

    form = InputMailForm(request.POST or None)
    download_file = DownloadForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        form = InputMailForm()

    if download_file.is_valid():
        download_file.save()
        download_file = DownloadForm()

    try:
        mail_to_check = (MailForm.objects.order_by('-time_create')[0])
    except:
        mail_to_check = ""

    try:
        count_mails = MailForm.objects.count()
    except:
        count_mails = "0"

    try:
        count_files = ImportFile.objects.count()
    except:
        count_files = "0"

    method = check_email(str(mail_to_check))

    context = {"form": form,
               "last_mail": mail_to_check,
               "count_mails": count_mails,
               "method": method,
               "file": download_file,
               "count_files": count_files
               }

    return render(request, 'app1/index.html', context)

def CreateMail(request):

    form = InputMailForm(request.POST or None)
    download_file = DownloadForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        form = InputMailForm()

    if download_file.is_valid():
        download_file.save()
        download_file = DownloadForm()

    try:
        count_mails = MailForm.objects.count()
    except:
        count_mails = "0"

    try:
        count_files = ImportFile.objects.count()
    except:
        count_files = "0"


    context = {"form": form,
               "count_mails": count_mails,
               "file": download_file,
               "count_files": count_files
              }

    return render(request, 'app1/index.html', context)

def DownloadFile(request):

    form = InputMailForm(request.POST or None)
    download_file = DownloadForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        form = InputMailForm()

    if download_file.is_valid():
        download_file.save()
        download_file = DownloadForm()

    try:
        count_mails = MailForm.objects.count()
    except:
        count_mails = "0"

    try:
        file_to_check = (MailForm.objects.order_by('-time_create')[0])
    except:
        file_to_check = ""

    try:
        count_files = ImportFile.objects.count()
    except:
        count_files = "0"

    result_file = check_file(str(ImportFile.objects.order_by('-file_create')[0]))

    try:
        pie_img = (ImageResult.objects.order_by('-img_create')[0])
    except:
        pie_img = ""

    result = result_file

    try:
        download_file = HttpResponse(result)
        download_file['Content-Disposition'] = 'attachment; filename=file_check_{0}.xlsx'.format(str(datetime.datetime.now())[:19].replace(':', ' '))
    except:
        download_file = None

    context = {"form": form,
               "count_mails": count_mails,
               "file": download_file,
               "last_file": file_to_check,
               "count_files": count_files,
               "pie_img": pie_img
               }

    return render(request, 'app1/index.html', context)

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена<h1>")

def find_last_file(path):

    dir_list = [os.path.join(path, x) for x in os.listdir(path)]

    if dir_list:
        date_list = [[x, os.path.getctime(x)] for x in dir_list]
        sort_date_list = sorted(date_list, key=lambda x: x[1], reverse=True)
    else:
        return None

    return sort_date_list[0][0]

def find_last_mail(folder):

    files = []

    for file in os.listdir(folder):
        full_path = os.path.join(folder, file)
        if os.path.isfile(full_path) and str(re.findall('mail', file)).replace("['", "").replace("']", "") == 'mail':
            files.append(full_path)

    if files:
        date_list = [[x, os.path.getctime(x)] for x in files]
        sort_date_list = sorted(date_list, key=lambda x: x[1], reverse=True)

    return (sort_date_list[0][0])