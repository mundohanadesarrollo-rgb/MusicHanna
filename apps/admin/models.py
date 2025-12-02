from django.db import models
from django.contrib.auth.models import User
from apps.users.models import Sede

# Create your models here.


class Artist(models.Model):
    """
    Modelo que representa a los artistas musicales.
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Artista")
    biografia = models.TextField(blank=True, null=True, verbose_name="Biografía")
    imagen = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL de Imagen")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Artista"
        verbose_name_plural = "Artistas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Album(models.Model):
    """
    Modelo que representa los álbumes musicales.
    """
    titulo = models.CharField(max_length=200, verbose_name="Título del Álbum")
    artista = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='albumes',
        verbose_name="Artista"
    )
    fecha_lanzamiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Lanzamiento")
    portada = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL de Portada")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Álbum"
        verbose_name_plural = "Álbumes"
        ordering = ['-fecha_lanzamiento']

    def __str__(self):
        return f"{self.titulo} - {self.artista.nombre}"


class Song(models.Model):
    """
    Modelo que representa las canciones/tracks.
    """
    titulo = models.CharField(max_length=200, verbose_name="Título de la Canción")
    artista = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='canciones',
        verbose_name="Artista"
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='canciones',
        verbose_name="Álbum"
    )
    duracion = models.DurationField(verbose_name="Duración")
    archivo_audio = models.FileField(
        upload_to='canciones/',
        blank=True,
        null=True,
        verbose_name="Archivo de Audio"
    )
    imagen = models.ImageField(
        upload_to='portadas/',
        blank=True,
        null=True,
        verbose_name="Imagen de Portada"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    publicado = models.BooleanField(default=False, verbose_name="Publicado")
    reproducciones = models.IntegerField(default=0, verbose_name="Reproducciones")
    likes = models.IntegerField(default=0, verbose_name="Likes")

    class Meta:
        verbose_name = "Canción"
        verbose_name_plural = "Canciones"
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.titulo} - {self.artista.nombre}"

    def incrementar_reproducciones(self):
        """Incrementa el contador de reproducciones."""
        self.reproducciones += 1
        self.save(update_fields=['reproducciones'])

    def incrementar_likes(self):
        """Incrementa el contador de likes."""
        self.likes += 1
        self.save(update_fields=['likes'])


class Playlist(models.Model):
    """
    Modelo que representa las listas de reproducción.
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Playlist")
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='playlists',
        verbose_name="Usuario Creador"
    )
    canciones = models.ManyToManyField(
        Song,
        related_name='playlists',
        blank=True,
        verbose_name="Canciones"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    publica = models.BooleanField(default=True, verbose_name="Pública")

    class Meta:
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"

    def total_canciones(self):
        """Retorna el total de canciones en la playlist."""
        return self.canciones.count()


class Play(models.Model):
    """
    Modelo que registra las reproducciones de canciones.
    Útil para estadísticas y análisis.
    """
    cancion = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='reproducciones_registradas',
        verbose_name="Canción"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reproducciones',
        verbose_name="Usuario"
    )
    sede = models.ForeignKey(
        Sede,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reproducciones',
        verbose_name="Sede"
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Reproducción"
        verbose_name_plural = "Reproducciones"
        ordering = ['-fecha_hora']

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return f"{self.cancion.titulo} - {usuario_str} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"
