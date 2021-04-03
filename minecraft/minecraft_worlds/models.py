from django.db import models
from django.core.validators import FileExtensionValidator


class World(models.Model):
    name = models.CharField(verbose_name='Nome', max_length=100)
    file = models.FileField(verbose_name='Arquivo', validators=[FileExtensionValidator(allowed_extensions=['zip'])])
    path = models.CharField(verbose_name='Caminho interno do mundo', max_length=200)
    active = models.BooleanField(default=False, verbose_name='False')