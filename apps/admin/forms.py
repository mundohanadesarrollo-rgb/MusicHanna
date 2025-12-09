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
        fields = ['nombre', 'estado', 'direccion', 'ciudad', 'usuario']
        labels = {
            'usuario': 'Usuario asignado',
        }
        widgets = {
            'usuario': forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('new_username')
        pwd = cleaned.get('new_password')
        pwd2 = cleaned.get('new_password_confirm')

        if username:
            # if creating a user, password is required and must match
            if not pwd:
                self.add_error('new_password', 'La contraseña es requerida cuando se crea un usuario.')
            if pwd and pwd2 and pwd != pwd2:
                self.add_error('new_password_confirm', 'Las contraseñas no coinciden.')
        
        # If not creating a new user, try to resolve `usuario_display` to a User instance
        usuario_display = cleaned.get('usuario_display')
        
        # Avoid resolving usuario when a new user will be created.
        # Also, don't do anything if a user is already resolved from the hidden 'usuario' input.
        if not username and usuario_display and not cleaned.get('usuario'):
            try:
                user = User.objects.get(username=usuario_display)
                cleaned['usuario'] = user
            except User.DoesNotExist:
                # Don't raise an error here.
                # This could be a username change for an existing user associated with the Sede.
                # The view contains the logic to handle this specific case.
                pass

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si la instancia ya tiene usuario asignado, mostrar su username en el campo de texto
        instance = kwargs.get('instance') or getattr(self, 'instance', None)
        if instance and getattr(instance, 'usuario', None):
            self.fields['usuario_display'].initial = instance.usuario.username