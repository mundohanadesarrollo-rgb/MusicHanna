from django import forms
from .models import Song
from apps.users.models import Sede

class SongForm(forms.ModelForm):
    artist_name = forms.CharField(max_length=200, label="Artista")
    album_title = forms.CharField(max_length=200, label="Álbum", required=False)
    duracion = forms.DurationField(required=False)

    class Meta:
        model = Song
        fields = ['titulo', 'artist_name', 'album_title', 'imagen', 'archivo_audio', 'duracion']


class SedeForm(forms.ModelForm):
    class Meta:
        model = Sede
        fields = ['nombre', 'estado', 'direccion', 'ciudad', 'pais']