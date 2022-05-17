from django.contrib import admin
from .models import *
from import_export import *

# Register your models here.

admin.site.register(MailForm)
admin.site.register(MailFile)
admin.site.register(ImportFile)
admin.site.register(ExportFile)
admin.site.register(ImageResult)