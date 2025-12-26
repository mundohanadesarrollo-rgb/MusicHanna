from django import forms
from .models import Song
from apps.users.models import Sede
from django.contrib.auth.models import User
from apps.users.models import UserProfile

class SongForm(forms.ModelForm):
    artist_name = forms.CharField(max_length=200, label="Artista")
    album_title = forms.CharField(max_length=200, label="Álbum", required=False)
    duracion = forms.DurationField(required=False)

    class Meta:
        model = Song
        fields = ['titulo', 'artist_name', 'album_title', 'imagen', 'archivo_audio', 'duracion']


class SedeForm(forms.ModelForm):
    # Campo de texto para búsqueda/selección por nombre de usuario (mejor UX)
    usuario_display = forms.CharField(required=False, label='Usuario (buscar por nombre)')
    # Optional fields to create a new User when creating a Sede
    new_username = forms.CharField(required=False, max_length=150, label='Nuevo usuario',
                                   help_text='Usuario a crear y asociar a esta sede')
    new_password = forms.CharField(required=False, widget=forms.PasswordInput, label='Contraseña')
    new_password_confirm = forms.CharField(required=False, widget=forms.PasswordInput, label='Confirmar contraseña')

    class Meta:
        model = Sede
        fields = ['nombre', 'direccion', 'ciudad', 'usuario']
        labels = {
            'usuario': 'Usuario asignado',
        }
        widgets = {
            'usuario': forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get('new_password')
        pwd2 = cleaned.get('new_password_confirm')

        # Generic password matching check
        if pwd and pwd2 and pwd != pwd2:
            self.add_error('new_password_confirm', 'Las contraseñas no coinciden.')

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si la instancia ya tiene usuario asignado, mostrar su username en el campo de texto
        instance = kwargs.get('instance') or getattr(self, 'instance', None)
        if instance and getattr(instance, 'usuario', None):
            self.fields['usuario_display'].initial = instance.usuario.username