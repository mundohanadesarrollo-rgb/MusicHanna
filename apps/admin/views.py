from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.contrib import messages
from apps.users.models import Sede
from apps.admin.models import Song, Artist, Album
from .forms import SongForm
from mutagen.mp3 import MP3
import datetime

# Create your views here.

def format_duration(seconds):
    return str(datetime.timedelta(seconds=int(seconds)))

def admin_dashboard(request):
    # Fetch pending songs (not published) from database
    pending_songs = Song.objects.filter(publicado=False).select_related('artista')

    subidas_revision = [
        {
            'id': song.id,
            'name': song.titulo,
            'author': song.artista.nombre,
            'fecha_subida': song.fecha_subida.strftime('%Y-%m-%d'),
            'image': song.imagen.url if song.imagen else static('images/default_album_art.png'),
        }
        for song in pending_songs
    ]

    # Fetch sedes from database
    sedes = Sede.objects.all()
    actividad_reciente = []
    for sede in sedes:
        actividad_reciente.append({
            'nro_sede': sede.id,
            'name': sede.nombre,
            'author': 'MusicHanna Admin',  # Default author since Sede model doesn't have one
            'status': sede.estado,
            'image': 'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=200&q=80',  # Default image
        })

    sedes_totales = len(actividad_reciente)
    nuevos_registros = len(subidas_revision)

    return render(
        request,
        'admin/dashboard.html',
        {
            'subidas_revision': subidas_revision,
            'actividad_reciente': actividad_reciente,
            'sedes_totales': sedes_totales,
            'nuevos_registros': nuevos_registros,
        },
    )

def admin_sedes(request):
    sedes = [
        {
            'nombre': 'Sede Principal - Centro',
            'estado': 'Activo',
            'badge_class': 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-200 text-green-800 dark:bg-green-900 dark:text-green-200',
            'dot_class': 'w-2 h-2 rounded-full bg-green-500',
            'ultima_actualizacion': '2023-10-26 10:00 AM',
        },

        

    ]

    subidas = {
        'name_page': 'Gestión Sedes',
        
    }

    return render(
        request,
        'admin/admin_sedes.html',
        {
            'subidas': subidas,
            'sedes': sedes
        },
    )

def admin_uploads(request):
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            # Obtener o crear Artista
            artist_name = form.cleaned_data['artist_name']
            artist, _ = Artist.objects.get_or_create(nombre=artist_name)

            # Obtener o crear Álbum (si se proporcionó)
            album_title = form.cleaned_data['album_title']
            album = None
            if album_title:
                album, _ = Album.objects.get_or_create(titulo=album_title, artista=artist)

            # Crear la instancia de Song pero no guardarla aún
            song = form.save(commit=False)
            song.artista = artist
            song.album = album

            # Calcular duración del audio
            audio_file = request.FILES['archivo_audio']
            try:
                audio = MP3(audio_file)
                song.duracion = datetime.timedelta(seconds=int(audio.info.length))
            except Exception as e:
                print(f"Error reading audio metadata: {e}")
                song.duracion = datetime.timedelta(seconds=0)

            song.save()
            messages.success(request, f"La canción '{song.titulo}' ha sido subida con éxito.")
            return redirect('admin_uploads')
        else:
            # Si el formulario no es válido, obtenemos las canciones y volvemos a renderizar la página
            # pasando el formulario con los errores.
            messages.error(request, "No se pudo subir la canción. Por favor, revisa los errores en el formulario.")
            uploads = Song.objects.select_related('artista', 'album').all()
            return render(request, 'admin/admin_uploads.html', {
                'uploads': uploads,
                'form': form
            })
        # Si el formulario no es válido, se renderizará la página de nuevo mostrando los errores (si los configuras en la plantilla)
    else:
        form = SongForm()

    # Para peticiones GET, obtenemos todas las canciones
    uploads = Song.objects.select_related('artista', 'album').all()

    
        
    return render(request, 'admin/admin_uploads.html', {
        'uploads': uploads,
        'form': form # Pasamos el formulario a la plantilla
    })

def admin_players(request, song_id=None):
    # Obtenemos todas las canciones, la más reciente primero
    all_songs = Song.objects.select_related('artista', 'album').all().order_by('-fecha_subida')

    if not all_songs.exists():
        return render(request, 'admin/admin_players.html', {'current_song': None})

    current_song = None
    if song_id:
        # Si se proporciona un ID, intenta encontrar esa canción
        current_song = all_songs.filter(id=song_id).first()

    if not current_song:
        # Si no se proporciona ID o no se encuentra, usa la más reciente
        current_song = all_songs.first()

    # La lista de reproducción son todas las canciones excepto la actual
    playlist = all_songs.exclude(id=current_song.id)
    
    # Reordenamos la lista completa para que la canción actual esté al principio para el JS
    songs_for_js = sorted(all_songs, key=lambda x: x.id != current_song.id)

    return render(request, 'admin/admin_players.html', 
                  {
                      'current_song': current_song,
                      'playlist': playlist,
                      'all_songs_json': [
                          {
                              'id': s.id, 'titulo': s.titulo, 'artista': s.artista.nombre, 
                              'imagen': s.imagen.url if s.imagen else static('images/default_album_art.png'), 
                              'audio': s.archivo_audio.url if s.archivo_audio else ''
                          }
                          for s in songs_for_js
                      ]
                  })

def admin_delete_song(request, song_id):
    # Solo permitir peticiones POST por seguridad
    if request.method == 'POST':
        song = get_object_or_404(Song, id=song_id)
        
        # Eliminar archivos asociados del almacenamiento, solo si son locales
        if song.archivo_audio and hasattr(song.archivo_audio, 'path'):
            try:
                song.archivo_audio.delete(save=False)
            except Exception as e:
                print(f"No se pudo eliminar el archivo de audio: {e}")
        if song.imagen and hasattr(song.imagen, 'path'):
            try:
                song.imagen.delete(save=False)
            except Exception as e:
                print(f"No se pudo eliminar el archivo de imagen: {e}")
            
        song.delete()
        messages.success(request, f"La canción '{song.titulo}' ha sido eliminada con éxito.")
    return redirect('admin_uploads')

def admin_login(request):
    return render(request, 'admin/login.html')

def admin_logout(request):

    
    return render(request, 'admin/logout.html')
