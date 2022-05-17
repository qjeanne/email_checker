
from django import forms
from .models import *
import datetime
class InputMailForm(forms.Form):

    text_mail = forms.CharField(max_length=100)
    time_create = str(datetime.datetime.now())

    # MailForm - наша маодель из models
    def save(self):
        new_tag = MailForm.objects.create(
            text_mail=self.cleaned_data['text_mail'],
            time_create=str(datetime.datetime.now())
        )
        return new_tag


class DownloadForm(forms.ModelForm):
    class Meta:
        model = ImportFile
        fields = ('file_name',)

class UploadForm(forms.ModelForm):
    class Meta:
        model = ExportFile
        fields = ('file_name',)

