import base64
import re
from io import BytesIO

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from itertools import groupby

from django.core.files.base import ContentFile

from .forms import *
import os
import datetime
from django.core.files import File
from .models import *
import matplotlib.pyplot as plt

from email_validator import validate_email, caching_resolver
import freemail
import threading
from email_validate import validate_or_fail, exceptions

import time

dfs = []
to_recheck = []


def check(email, recheck):

    global to_recheck

    DNS_errors = {'DomainNotFoundError': 'Домен адреса электронной почты не может быть найден.',
                  'NoNameserverError': 'Для домена нет сервера имен.',
                  'DNSTimeoutError': 'Истекло время ожидания при запросе сервера имен.',
                  'DNSConfigurationError': 'Сервер имен настроен неправильно.',
                  'NoMXError': 'Сервер имен не содержит записей MX для домена.',
                  'NoValidMXError': 'Сервер имен перечисляет записи MX для домена, но ни одна из них не является допустимой.'
                  }
    SMTP_errors = {'AddressNotDeliverableError': 'Сервер SMTP отказался давать доступ к проверяемому адресу электронной почты.',
                   'SMTPCommunicationError': 'Сервер SMTP не дает добраться до точки, где можно спросить его об адресе электронной почты.',
                   'SMTPTemporaryError': 'Произошла ошибка при проверке всех доступных MX-серверов.'
                   }
    more_SMTP_info = {421: ' Работа с сервером невозможна.',
                      450: ' Запрошенная команда не принята – недоступен почтовый ящик.',
                      454: ' Аутентификация невозможна по причине временного сбоя сервера.',
                      530: ' Сервер требует аутентификации для выполнения запрошенной команды.',
                      534: ' Выбранный механизм аутентификации для данного пользователя является не достаточно надежным.',
                      535: ' Аутентификация отклонена сервером.',
                      538: ' Выбранный метод аутентификации возможен только при зашифрованном канале связи.',
                      550: ' Почтовый ящик недоступен (команда отклонена локальной политикой безопасности либо почтовый адрес не существует).',
                      551: ' Нелокальный пользователь.'
                      }

    result = {'Email': email,
              'Проверка синтаксиса': False,
              'Проверка MX-записей': False,
              'MX-записи': None,
              'SMTP-аутентификация': False,
              'Free-email': None,
              'Временный email': None,
              'Ошибка': None}

    try:
        if validate_or_fail(email, check_blacklist=False):
            email_object = validate_email(email, dns_resolver=resolver)
            result['Проверка синтаксиса'] = True
            result['Проверка MX-записей'] = True
            list_of_mx = []
            for mx in email_object.mx:
                list_of_mx.append(mx[1])
            result['MX-записи'] = '\n'.join(list_of_mx)
            result['SMTP-аутентификация'] = True
            result['Free-email'] = freemail.is_free(email)
            result['Временный email'] = freemail.is_disposable(email)
    except Exception as e:
        if e.__class__.__name__ == 'AddressFormatError':
            result['Ошибка'] = 'Email-адрес не прошел проверку синтаксиса'
        else:
            result['Проверка синтаксиса'] = True
            if e.__class__.__name__ in DNS_errors:
                result['Ошибка'] = DNS_errors[e.__class__.__name__]
            else:
                if e.__class__.__name__ == 'SMTPTemporaryError' and recheck == False:
                    to_recheck.append(email)
                    return None
                email_object = validate_email(email, dns_resolver=resolver)
                result['Проверка MX-записей'] = True
                result['Free-email'] = freemail.is_free(email)
                result['Временный email'] = freemail.is_disposable(email)
                list_of_mx = []
                for mx in email_object.mx:
                    list_of_mx.append(mx[1])
                result['MX-записи'] = '\n'.join(list_of_mx)
                result['Ошибка'] = SMTP_errors[e.__class__.__name__]
                codes = []
                for x in e.args:
                    for mes in dict(x).values():
                        code = mes.code
                        if code not in codes:
                            codes.append(code)
                            if code in more_SMTP_info.keys():
                                result['Ошибка'] += more_SMTP_info[code]

    return result

def determine_email_status(result):
    if result['SMTP-аутентификация']:
        result['Статус'] = 'Активный'
    elif result['Ошибка'] == 'Произошла ошибка при проверке всех доступных MX-серверов.':
        result['Статус'] = 'Неактивный'
    elif result['Проверка MX-записей']:
        result['Статус'] = 'Несуществующий или закрытый'
    elif result['Проверка синтаксиса']:
        result['Статус'] = 'Несуществующий'
    else:
        result['Статус'] = 'Некорректный'

def check_and_append_to_list(email, recheck):
    global dfs
    res = check(email, recheck)
    if res is not None:
        determine_email_status(res)
        dfs.append(res)


resolver = caching_resolver(timeout=10)
# ------------------------------ ФУНКЦИЯ ОБРАБОТКИ ЕДЕНИЧНОГО E-MAIL --------------------------
def CreateTable(email):

    dfs.clear()
    to_recheck.clear()

    if email == "":
        return None

    check_and_append_to_list(email, False)

    for email in to_recheck:
        check_and_append_to_list(email, True)

    df = pd.DataFrame(dfs)

    # -------------------------------- СОХРАНЕНИЕ ОБРАБОТАННОЙ ПОЧТЫ В БД ----------------------------------------

    filename = ('mail_{0} {1}.xlsx'.format(email, str(datetime.datetime.now())[:19].replace(':', ' ')))
    df.to_excel(filename, index=False)

    try:
        with open(filename, 'rb') as model_excel:
            model_object = ExportFile()
            model_object.file_name.save(filename, File(model_excel))
    except:
        print("\nНе удалось сохранить ОБРАБОТАННЫЙ ФАЙЛ {0} в БД!\n".format(filename))

    return dfs[0]
# ------------------------------------ ФУНКЦИЯ ОБРАБОТКИ ЗАГРУЖЕННОГО ФАЙЛА ----------------------------
def MailProcessing(last_file):

    dfs.clear()
    to_recheck.clear()
    threads = []

    # читаем данные из последнего загруженного файла
    if last_file.endswith('.xlsx') == True:
        input_df = pd.read_excel(last_file, sep=';', encoding='utf-8')
    elif last_file.endswith('.csv') == True:
        input_df = pd.read_csv(last_file, sep=';', encoding='utf-8')

    for email in input_df['Email']:
        t = threading.Thread(target=check_and_append_to_list, args=(email, False))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    threads.clear()

    for email in to_recheck:
        t = threading.Thread(target=check_and_append_to_list, args=(email, True))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    df = pd.DataFrame(dfs)

    list_active = []
    list_unactive = []
    list_lock = []
    list_unexist = []
    list_incorrectly = []

    for email in dfs:
        if email['Статус'] == 'Активный':
            list_active.append(email)
        elif email['Статус'] == 'Неактивный':
            list_unactive.append(email)
        elif email['Статус'] == 'Несуществующий или закрытый':
            list_lock.append(email)
        elif email['Статус'] == 'Несуществующий':
            list_unexist.append(email)
        elif email['Статус'] == 'Некорректный':
            list_incorrectly.append(email)

    df_active = pd.DataFrame(list_active)
    df_unactive = pd.DataFrame(list_unactive)
    df_lock = pd.DataFrame(list_lock)
    df_unexist = pd.DataFrame(list_unexist)
    df_incorrectly = pd.DataFrame(list_incorrectly)

    df_mass = [len(list_active), len(list_unactive), len(list_lock), len(list_unexist), len(list_incorrectly)]


    # формируем словарик состоящий из названия будущих Excel-листов и датафреймов
    ITOG = {'Активные': df_active, 'Неактивные': df_unactive, 'Несуществующие или закрытые': df_lock,
            'Несуществующие': df_unexist, 'Некорректные': df_incorrectly}

    # создаём директорию для хранения построенных диаграмм
    dir = 'app1/static/app1/upload_files/'

    if not os.path.exists(dir):
        os.makedirs(dir)

    # обзовём наш файл
    filename_excel = dir + ('Результаты обработки {0}.xlsx'.format(str(datetime.datetime.now())[:19].replace(':', ' ')))

    writer = pd.ExcelWriter(filename_excel, engine='xlsxwriter', options={'nan_inf_to_errors': True})

    workbook = writer.book

    for i in ITOG.keys():

        if ITOG[i].empty:
            print("\n{0} отсутствуют\n".format(i))

        else:

            ITOG[i].to_excel(writer, sheet_name = i, index=False)

            # Настройка ширины столбцов
            my_format = writer.book.add_format({'num_format': '#', 'bold': False, 'font_name': 'Times New Roman',  'font_color': '#000000', 'font_size': 10, 'text_wrap': False, 'align': 'center', 'valign': 'vcenter', 'border': 3, 'border_color': '#cccccc'}) #'fg_color': '#bee3f7',
            # настройка масштаба excel таблицы

            writer.sheets['{0}'.format(i)].set_zoom(95)
            # настройка ширины столбцов excel таблицы
            writer.sheets['{0}'.format(i)].set_column('A:W', 30, my_format)

            # РАСКРАШИВАЕМ КЛЕТКИ градиентом
            worksheet = writer.sheets['{0}'.format(i)]

    writer.save()

# -------------------------------- СОХРАНЕНИЕ ОБРАБОТАННОГО ФАЙЛА В БД ----------------------------------------

    name = ('Результаты обработки {0}.xlsx'.format(str(datetime.datetime.now())[:19].replace(':', ' ')))
    try:
        with open(filename_excel, 'rb') as model_excel:
            model_object = ExportFile()
            model_object.file_name.save(name, File(model_excel))
    except:
        print("\nНе удалось сохранить ОБРАБОТАННЫЙ ФАЙЛ {0} в БД!\n".format(name))


# ------------------------------- СТРОИМ ДИАГРАММУ РАЗДЕЛЕНИЯ НА ГРУППЫ И СОХРАНЯЕМ ЕЁ В БД -----------------------

    x = df_mass
    labels = ['Активные', 'Неактивные', 'Несуществующие или закрытые', 'Несуществующие', 'Некорректные']
    colors = ['#009D66', '#D7CB12', 'gray', '#427CA6', '#A61000']

    df_graph = pd.DataFrame({"x": df_mass,
                             "labels": labels})

    df_graph = df_graph[df_graph.x != 0]


    fig, ax = plt.subplots()
    patches, texts, pcts = ax.pie(
        df_graph.x,
        colors=colors,
        autopct='%.1f%%',
        pctdistance=0.75,
        wedgeprops={'linewidth': 2.0, 'edgecolor': 'white', 'width': 0.5},
        textprops={'fontsize': 12},
        startangle=90)
    for i, patch in enumerate(patches):
        texts[i].set_color(patch.get_facecolor())
    plt.setp(pcts, color='white')
    plt.legend(loc='upper center', labels=labels, colors=colors, bbox_to_anchor = (0.1, 1.05),)
    #ax.set_title('Диаграмма разделения email-адресов на группы', fontsize=16)
    plt.tight_layout()

    # сохраняем диаграмму в БД
    imgdata = BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    pie_results = imgdata.getvalue()
    b64 = base64.b64encode(pie_results).decode()

    content_file = ContentFile(pie_results)
    model_object = ImageResult()
    model_object.img_name.save('Диаграмма результатов анализа email-адресов {0}.png'.format(str(datetime.datetime.now())[:19].replace(':', ' ')), content_file)
    model_object.save()


