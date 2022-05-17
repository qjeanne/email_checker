from django.db import models

class Users(models.Model):
    UserID = models.AutoField('UserID', primary_key=True)
    Login = models.CharField('Login', max_length=150, unique=True)
    Password = models.CharField('Password', max_length=20)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "users"

class Diagrams(models.Model):
    DiagramID = models.AutoField('DiagramID', primary_key=True)
    Path = models.ImageField('Path', upload_to='app1/static/app1/img/')

    class Meta:
        verbose_name = "Diagram"
        verbose_name_plural = "Diagrams"
        db_table = "diagrams"

class EmailFiles(models.Model):
    EmailFileID = models.AutoField(primary_key=True)
    DiagramID = models.OneToOneField(Diagrams, on_delete=models.SET_NULL, null=True)
    UserID = models.OneToOneField(Users, on_delete=models.CASCADE, null=True)
    FileName = models.CharField('FileName', max_length=100)

    class Meta:
        verbose_name = "EmailFile"
        verbose_name_plural = "EmailFiles"
        db_table = "email_files"

class Emails(models.Model):
    EmailID = models.AutoField(primary_key=True)
    EmailFileID = models.OneToOneField(EmailFiles, on_delete=models.CASCADE, null=True)
    UserID = models.OneToOneField(Users, on_delete=models.CASCADE, null=True)
    Email = models.CharField('Email', max_length=150)
    SyntaxCheck = models.BooleanField('SyntaxCheck')
    MXCheck = models.BooleanField('MXCheck')
    MXNotes = models.TextField('MXCheck', null=True)
    SMTPCheck = models.BooleanField('SMTPCheck')
    Free = models.BooleanField('Free', null=True)
    Temp = models.BooleanField('Temp', null=True)
    Error = models.TextField('Error', null=True)
    Status = models.CharField('Status', max_length=100)

    class Meta:
        verbose_name = "Emails"
        verbose_name_plural = "Emails"
        db_table = "emails"

# БД для загрузки одиночной проверки
class MailForm(models.Model):
    text_mail = models.CharField('Emails', max_length=100)
    time_create = models.CharField('Время записи данных', max_length=100)

    def __str__(self):
        return self.text_mail

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"
        db_table = "input_mails"



# БД для загрузки почт из файла
class MailFile(models.Model):
    text_mail = models.CharField('Emails', max_length=100)
    time_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text_mail

    class Meta:
        verbose_name = "Email file"
        verbose_name_plural = "Email files"
        db_table = "file_mails"


# БД для загрузки файла
class ImportFile(models.Model):
    file_name = models.FileField('', upload_to='app1/static/app1/download_files/')
    file_create = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField('Регистрация изменений', default=False)

    def __str__(self):
        return "{}".format(self.file_name)

    class Meta:
        verbose_name = "Upload file"
        verbose_name_plural = "Upload files"
        db_table = "import_files"


# БД для загрузки обработанных файлов
class ExportFile(models.Model):
    file_name = models.FileField('', upload_to='app1/static/app1/upload_files/')
    file_create = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField('Регистрация изменений', default=False)

    def __str__(self):
        return "{}".format(self.file_name)

    class Meta:
        verbose_name = "Result file"
        verbose_name_plural = "Result files"
        db_table = "file_results"


# БД для загрузки обработанных файлов
class ImageResult(models.Model):
    img_name = models.ImageField('', upload_to='app1/static/app1/img/')
    img_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.img_name)

    class Meta:
        verbose_name = "Results chart"
        verbose_name_plural = "Results charts"
        db_table = "img_results"
