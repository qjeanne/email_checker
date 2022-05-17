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


    # ----------------- ОБРАБОТКА ФОРМЫ ------------------
def CreateMail(request):

    # проверка типа запроса на сервер
    form = InputMailForm(request.POST or None)
    download_file = DownloadForm(request.POST or None, request.FILES or None)

    # сохранение введённой формы
    if form.is_valid():
        form.save()
        form = InputMailForm()

    # сохранение информации о файле
    if download_file.is_valid():
        download_file.save()
        download_file = DownloadForm()

    # последняя запись E-Mail
    try:
        last_mail = (MailForm.objects.order_by('-time_create')[0])
    except:
        last_mail = ""

    # сколько всего загружено почт
    try:
        count_mails = MailForm.objects.count()
    except:
        count_mails = "0"

    # последняя запись загруженного файла
    try:
        last_file = (ImportFile.objects.latest('file_name'))
    except:
        last_file = ""

    # сколько всего загружено файлов
    try:
        count_files = ImportFile.objects.count()
    except:
        count_files = "0"

    try:
        method = CreateTable(str(last_mail))
    except:
        method = ""


    # вызов функции обработки диаграммы
    try:
        pie_img = (ImageResult.objects.order_by('-img_create')[0])
    except:
        pie_img = ""


    context = {"form": form,
               "last_mail": last_mail,
               "count_mails": count_mails,
               "method": method,
               "file": download_file,
               "last_file": last_file,
               "count_files": count_files,
               "pie_img": pie_img
              }

    return render(request, 'app1/index.html', context)

def DownloadFile(request):

    try:
        result_file = MailProcessing(ImportFile.objects.latest('file_name'))
    except:
        result_file = ""

    path = 'app1/static/app1/upload_files/'

    # with open(find_last_file(path), 'rb') as model_excel:
    #     result = model_excel.read()

    result = result_file

    try:
        download_file = HttpResponse(result)
        download_file['Content-Disposition'] = 'attachment; filename=Mails Result {0}.xlsx'.format(str(datetime.datetime.now())[:19].replace(':', ' '))
    except:
        download_file = None

    return download_file

def UploadMail(request):
    # последняя запись E-Mail
    try:
        last_mail = (MailForm.objects.order_by('-time_create')[0])
    except:
        last_mail = ""

    method = CreateTable(str(last_mail))

    return render(request, 'app1/index.html', {"method": method})



# Обработчик ошибок
# Если страница не найдена
def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена<h1>")


# функция поиска последнего загруженного файла в папке
def find_last_file(path):

    # Получим список имен всего содержимого папки и превратим их в абсолютные пути
    dir_list = [os.path.join(path, x) for x in os.listdir(path)]

    if dir_list:
        # Создадим список из путей к файлам и дат их создания.
        date_list = [[x, os.path.getctime(x)] for x in dir_list]
        # Отсортируем список по дате создания в обратном порядке
        sort_date_list = sorted(date_list, key=lambda x: x[1], reverse=True)
        # Выведем первый элемент списка. Он и будет самым последним по дате

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

        # Создадим список из путей к файлам и дат их создания.
        date_list = [[x, os.path.getctime(x)] for x in files]

        # Отсортируем список по дате создания в обратном порядке
        sort_date_list = sorted(date_list, key=lambda x: x[1], reverse=True)

    return (sort_date_list[0][0])