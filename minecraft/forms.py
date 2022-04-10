from django import forms
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    if not value.name.endswith('.mcaddon') and not value.name.endswith('.mcpack') and not value.name.endswith('.zip'):
        raise ValidationError(u'Somente arquivos mcaddon, mcpack e zip são permitidos')

class UploadAddonForm(forms.Form):
    name = forms.CharField(required=True, help_text='Nome único para o addon')
    addon_type = forms.ChoiceField(choices=(('behavior', 'Behavior Pack'), ('resource', 'Resource Pack')), help_text='Envie somente Behavior ou Resource packs, envio de mcaddon completo não é suportado. Descompacte antes')
    file = forms.FileField(validators=[validate_file_extension], required=True)