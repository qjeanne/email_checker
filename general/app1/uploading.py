# import os
# import sys
#
# os.environ['DJANGO_SETTINGS_MODULE'] = "general.settings"
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
#
# from .models import *
# import xlrd
# import django
# django.setup()
#
#
#
# class UploadingProducts(object):
#     foreign_key_fields = ["category"]
#     model = ImportMailForm
#
#     def __init__(self, data):
#         data = data
#         self.uploading_file = data.get("file")
#         self.parsing()
#
#     def getting_related_model(self, field_name):
#         related_model = self.model._meta.get_field(field_name).rel.to
#         return related_model
#
#     def getting_headers(self):
#         s = self.s
#         headers = dict()
#         for column in range(s.ncols):
#             value = s.cell(0, column).value
#             headers[column] = value
#         return headers
#
#     def parsing(self):
#         uploading_file = self.uploading_file
#         wb = xlrd.open_workbook(file_contents=uploading_file.read())
#         s = wb.sheet_by_index(0)
#         self.s = s
#
#         headers = self.getting_headers()
#         print(headers)
#
#         product_bulk_list = list()
#         for row in range(1, s.nrows):
#             row_dict = {}
#             for column in range(s.ncols):
#                 value = s.cell(row, column).value
#                 field_name = headers[column]
#
#                 if field_name == "id" and not value:
#                     continue
#                 if field_name in self.foreign_key_fields:
#                     related_model = self.getting_related_model(field_name)
#                     print(related_model)
#
#                     instance, created = related_model.objects.get_or_create(name=value)
#                     value = instance
#
#                 row_dict[field_name] = value
#
#             print(row_dict)
#             product_bulk_list.append(ImportMailForm(**row_dict))
#             #ImportMailForm.objects.create(**row_dict)
#
#         ImportMailForm.objects.bulk_create(product_bulk_list)
#         return True