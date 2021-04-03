from django.db import models
from django.core.validators import FileExtensionValidator


class Addon(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nome')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')
    date_modified = models.DateTimeField(auto_now=True, verbose_name='Data de alteração')


class BehaviorPack(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    pack = models.FileField(verbose_name='Arquivo do Behavior Pack', validators=[FileExtensionValidator(allowed_extensions=['zip'])])
    active = models.BooleanField(default=False, verbose_name='Ativo')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')
    date_modified = models.DateTimeField(auto_now=True, verbose_name='Data de alteração')
    addon = models.ForeignKey(Addon, null=True, default=None, verbose_name='Addon', related_name='behavior_packs')


class ResourcePack(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    pack = models.FileField(verbose_name='Arquivo do Resource Pack', validators=[FileExtensionValidator(allowed_extensions=['zip'])])
    active = models.BooleanField(default=False, verbose_name='Ativo')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')
    date_modified = models.DateTimeField(auto_now=True, verbose_name='Data de alteração')
    addon = models.ForeignKey(Addon, null=True, default=None, verbose_name='Addon', related_name='resource_packs')

