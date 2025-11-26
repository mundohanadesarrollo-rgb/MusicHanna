from django.contrib import admin
from .models import Artist, Album, Song, Playlist, Play

# Register your models here.


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion')
    search_fields = ('nombre', 'biografia')
    ordering = ('nombre',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'fecha_lanzamiento', 'fecha_creacion')
    list_filter = ('artista', 'fecha_lanzamiento')
    search_fields = ('titulo', 'artista__nombre')
    ordering = ('-fecha_lanzamiento',)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'album', 'duracion', 'publicado', 'reproducciones', 'likes', 'fecha_subida')
    list_filter = ('publicado', 'artista', 'album', 'fecha_subida')
    search_fields = ('titulo', 'artista__nombre', 'album__titulo')
    ordering = ('-fecha_subida',)
    readonly_fields = ('reproducciones', 'likes', 'fecha_subida')


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'publica', 'fecha_creacion', 'total_canciones')
    list_filter = ('publica', 'fecha_creacion')
    search_fields = ('nombre', 'usuario__username')
    filter_horizontal = ('canciones',)
    ordering = ('-fecha_creacion',)


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ('cancion', 'usuario', 'sede', 'fecha_hora')
    list_filter = ('sede', 'fecha_hora')
    search_fields = ('cancion__titulo', 'usuario__username', 'sede__nombre')
    ordering = ('-fecha_hora',)
    readonly_fields = ('fecha_hora',)
