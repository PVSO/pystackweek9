from django.contrib.auth.models import User
from django.db import models


class Apostila(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=100)
    arquivo = models.FileField(upload_to='add_apostila')

    def __str__(self):
        return self.titulo


class ViewApostilas(models.Model):
    ip = models.GenericIPAddressField()
    apostila = models.ForeignKey(Apostila, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.ip
