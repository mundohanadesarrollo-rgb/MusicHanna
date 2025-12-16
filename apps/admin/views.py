from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.contrib import messages
import logging
from apps.users.models import Sede
from apps.admin.models import Song, Artist, Album, Play
from django.contrib.auth.models import User
from apps.users.models import UserProfile
from django.utils import timezone
from .forms import SongForm
from mutagen.mp3 import MP3
import datetime
import os
import json
# Importación para manejar respuestas JSON
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json # Asegurarse que json está importado

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
            'fecha_subida': song.fecha_subida.strftime('%Y-%m-%d %I:%M %p'),
            'image': song.imagen.url if song.imagen else static('img/default_album_art.png'),
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

    # Get the sede for the player.
    current_sede = None
    print("DEBUG: Searching for a Sede for the player.")
    if request.user.is_authenticated:
        print(f"DEBUG: User '{request.user.username}' is authenticated.")
        try:
            current_sede = request.user.profile.sede
            if current_sede:
                print(f"DEBUG: Found Sede '{current_sede.nombre}' via user profile.")
        except (UserProfile.DoesNotExist, Sede.DoesNotExist, AttributeError):
             try:
                current_sede = request.user.sede
                if current_sede:
                    print(f"DEBUG: Found Sede '{current_sede.nombre}' via direct user relation.")
             except (Sede.DoesNotExist, AttributeError):
                current_sede = None

    if not current_sede:
        print("DEBUG: User does not have an associated Sede. Falling back to Sede.objects.first().")
        current_sede = Sede.objects.first()
        if current_sede:
            print(f"DEBUG: Fallback Sede is '{current_sede.nombre}'.")
        else:
            print("DEBUG: No Sedes found in the database. Player will not have a Sede ID.")

    return render(
        request,
        'admin/dashboard.html',
        {
            'subidas_revision': subidas_revision,
            'actividad_reciente': actividad_reciente,
            'sedes_totales': sedes_totales,
            'nuevos_registros': nuevos_registros,
            'sede': current_sede,
        },
    )

def admin_sedes(request):
    # Obtener sedes reales desde la base de datos y mapear al formato que usa la plantilla
    sedes_qs = Sede.objects.all()
    sedes = []
    for s in sedes_qs:
        # El estado de la sede y las clases visuales dependen directamente de s.estado
        is_active = (s.estado == 'activo')

        if is_active:
            estado_display = 'Activo'
            badge_class = 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-200 text-green-800 dark:bg-green-900 dark:text-green-200'
            dot_class = 'w-2 h-2 rounded-full bg-green-500'
        else:
            estado_display = 'Inactivo'
            badge_class = 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-200 text-red-800 dark:bg-red-900 dark:text-red-200'
            dot_class = 'w-2 h-2 rounded-full bg-red-500'

        # assigned user (direct field on Sede)
        usuario_username = s.usuario.username if getattr(s, 'usuario', None) else ''
        usuario_id = s.usuario.id if getattr(s, 'usuario', None) else None

        sedes.append({
            'id': s.id,
            'nombre': s.nombre,
            'estado': estado_display, # Usa el estado de la base de datos
            'is_active': is_active,
            'usuario': usuario_username,
            'usuario_id': usuario_id,
            'estado_raw': s.estado,
            'badge_class': badge_class,
            'dot_class': dot_class,
            'ultima_actualizacion': s.ultima_actualizacion.strftime('%Y-%m-%d %I:%M %p') if s.ultima_actualizacion else '',
            'fecha_creacion': s.fecha_creacion.strftime('%Y-%m-%d %I:%M %p') if s.fecha_creacion else '',
            'direccion': s.direccion or '',
            'ciudad': s.ciudad or '',
        })


    subidas = {
        'name_page': 'Gestión Sedes',
    }

    return render(
        request,
        'admin/admin_sedes.html',
        {
            'subidas': subidas,
            'sedes': sedes,
            'users': User.objects.all(),
        },
    )


def admin_edit_sede(request, sede_id=None):
    if sede_id:
        sede = get_object_or_404(Sede, id=sede_id)
    else:
        sede = None

    from .forms import SedeForm

    if request.method == 'POST':
        form = SedeForm(request.POST, instance=sede)
        
        # Debug: print POST keys
        try:
            print('DEBUG admin_edit_sede POST keys:', list(request.POST.keys()))
        except Exception:
            pass
        if form.is_valid():
            # Debug: print cleaned_data
            try:
                print('DEBUG SedeForm.cleaned_data:', form.cleaned_data)
            except Exception:
                pass
            # Prepare instance but don't commit yet because we may need to create a User
            instance = form.save(commit=False)

            new_username = form.cleaned_data.get('new_username')
            new_password = form.cleaned_data.get('new_password')

            # Debug: log cleaned_data for diagnosis
            try:
                logging.getLogger(__name__).debug('SedeForm.cleaned_data: %s', form.cleaned_data)
            except Exception:
                pass

            # Lógica de usuario unificada
            usuario_display = form.cleaned_data.get('usuario_display')
            usuario_id = request.POST.get('usuario') # ID del usuario del campo oculto

            if new_username: # 1. Prioridad: Crear un nuevo usuario (solo al añadir sede)
                if User.objects.filter(username=new_username).exists():
                    form.add_error('new_username', 'El nombre de usuario ya existe.')
                else:
                    user = User.objects.create_user(username=new_username, password=new_password)
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()
                    instance.usuario = user
            
            elif not usuario_id and usuario_display and sede and sede.usuario:
                # 2. Editando el nombre de un usuario existente
                # El ID del usuario no se envió, pero hay texto y una sede con usuario original
                original_username = sede.usuario.username
                if usuario_display != original_username:
                    # El nombre ha cambiado, intentamos actualizarlo
                    if User.objects.filter(username=usuario_display).exclude(pk=sede.usuario.pk).exists():
                        form.add_error('usuario_display', f'El nombre de usuario "{usuario_display}" ya existe.')
                    else:
                        sede.usuario.username = usuario_display
                        sede.usuario.save(update_fields=['username'])
                        instance.usuario = sede.usuario # Re-asignar por si acaso
                else:
                    # El nombre no cambió, mantenemos el usuario original
                    instance.usuario = sede.usuario
            else:
                # 3. Asignar un usuario existente (buscado) o desasignar
                usuario = form.cleaned_data.get('usuario') if hasattr(form, 'cleaned_data') else None
                if usuario:
                    instance.usuario = usuario # Asignar el usuario seleccionado
                else:
                    # Log that no usuario was provided in form.cleaned_data
                    logging.getLogger(__name__).debug('No usuario provided in form.cleaned_data')
                    # Si el campo de texto está vacío, se desasigna el usuario
                    if sede and not usuario_display:
                        instance.usuario = None

            if form.errors:
                 if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
                    return JsonResponse({'success': False, 'errors': errors}, status=400)

            instance.save()
            # Debug: print assigned user after save
            try:
                assigned_username = instance.usuario.username if getattr(instance, 'usuario', None) else None
                print('DEBUG assigned_username after save:', assigned_username)
            except Exception:
                assigned_username = None
            # Provide clearer feedback about assigned user
            if assigned_username:
                messages.success(request, f'Sede guardada correctamente. Usuario asignado: {assigned_username}')
            else:
                messages.success(request, 'Sede guardada correctamente. (Sin usuario asignado)')

            # Ensure a UserProfile exists and is linked to this sede for the user
            try:
                assigned_user = instance.usuario
                if assigned_user:
                    UserProfile.objects.update_or_create(user=assigned_user, defaults={'sede': instance})
            except Exception:
                # be liberal — profile isn't critical, ignore errors here
                pass
            # Si la petición es AJAX, devolver JSON para que el modal pueda manejarlo
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'success': True})
            messages.success(request, 'Sede guardada correctamente.')
            return redirect('admin_sedes')
        else:
            # Si es petición AJAX, devolver los errores en JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        initial_data = {}
        if sede and sede.usuario:
            pass # El precargado se hace en el JS del modal
        form = SedeForm(instance=sede, initial=initial_data)

    return render(request, 'admin/edit_sede.html', {'form': form, 'sede': sede})


def admin_delete_sede(request, sede_id):
    if request.method == 'POST':
        try:
            sede = get_object_or_404(Sede, id=sede_id)
            sede_nombre = sede.nombre 
            
            # 1. IDENTIFICAR EL USUARIO ASOCIADO
            # El campo de relación se llama 'usuario' en el modelo Sede
            user_to_delete = getattr(sede, 'usuario', None)

            # 2. ELIMINAR LA SEDE
            sede.delete()

            # 3. ELIMINAR EL USUARIO (si existía)
            if user_to_delete:
                user_to_delete_username = user_to_delete.username
                user_to_delete.delete()
                
                messages.success(request, f'Sede "{sede_nombre}" y usuario "{user_to_delete_username}" eliminados correctamente.')
            else:
                messages.success(request, f'Sede "{sede_nombre}" eliminada correctamente. No había usuario asociado.')
                
        except Sede.DoesNotExist:
             messages.error(request, 'Error: La sede que intentó eliminar no existe.')
        except Exception as e:
             messages.error(request, f'Ocurrió un error al intentar eliminar la sede: {e}')
             
    return redirect('admin_sedes')

# =========================================================================
# === NUEVA FUNCIÓN PARA REGISTRAR LA REPRODUCCIÓN (PLAY SIGNAL ENDPOINT) ===
# =========================================================================

@csrf_exempt
@require_POST
def play_signal(request):
    """
    Endpoint llamado por el reproductor de la sede (cliente) para registrar 
    que una canción acaba de comenzar a reproducirse. Esto actualiza el estado 'Activo'.
    """
    try:
        # Se asume que el body de la petición contiene JSON con 'sede_id' y 'song_id'
        data = json.loads(request.body.decode('utf-8'))
        sede_id = data.get('sede_id')
        song_id = data.get('song_id')

        if not sede_id or not song_id:
            return JsonResponse({'status': 'error', 'message': 'Faltan sede_id o song_id'}, status=400)

        # 1. Obtener la Sede y la Canción
        sede = Sede.objects.get(id=sede_id)
        song = Song.objects.get(id=song_id)
        
        # 2. Opcional: Obtener el usuario asociado a la sede para el registro
        user = getattr(sede, 'usuario', None)
        
        # 3. Crear el registro de Play
        Play.objects.create(
            cancion=song,
            sede=sede,
            usuario=user # Puede ser None si la sede no tiene usuario asignado
        )

        return JsonResponse({'status': 'success', 'message': 'Reproducción registrada.'})

    except Sede.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'Sede con ID {sede_id} no encontrada.'}, status=404)
    except Song.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'Canción con ID {song_id} no encontrada.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Cuerpo de petición JSON inválido.'}, status=400)
    except Exception as e:
        logging.error(f"Error al registrar play_signal: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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

    # Si la canción seleccionada no tiene archivo de audio, buscar la primera que sí lo tenga
    if not getattr(current_song, 'archivo_audio', None):
        song_with_audio = all_songs.filter(archivo_audio__isnull=False).exclude(id=current_song.id).first()
        if song_with_audio:
            current_song = song_with_audio

    # La lista de reproducción son todas las canciones excepto la actual
    playlist = all_songs.exclude(id=current_song.id)

    # Reordenamos la lista completa para que la canción actual esté al principio para el JS
    songs_for_js = sorted(all_songs, key=lambda x: x.id != current_song.id)

    # Filtrar canciones que realmente tienen archivo de audio disponible en disco/storage
    valid_songs_for_js = []
    for s in songs_for_js:
        try:
            has_audio = bool(s.archivo_audio and (hasattr(s.archivo_audio, 'path') and s.archivo_audio.storage.exists(s.archivo_audio.name)))
        except Exception:
            # fallback to checking filesystem path
            try:
                has_audio = bool(s.archivo_audio and s.archivo_audio.path and os.path.exists(s.archivo_audio.path))
            except Exception:
                has_audio = False
        if has_audio:
            valid_songs_for_js.append(s)

    # If current_song is not in valid_songs_for_js, try to pick the first valid song
    if current_song and current_song not in valid_songs_for_js:
        current_song = valid_songs_for_js[0] if valid_songs_for_js else None

    songs_for_js = valid_songs_for_js

    songs_list = [
        {
            'id': s.id,
            'titulo': s.titulo,
            'artista': s.artista.nombre,
            'imagen': s.imagen.url if s.imagen else static('img/default_album_art.png'),
            'audio': s.archivo_audio.url if s.archivo_audio else ''
        }
        for s in songs_for_js
    ]
    
    sede = None
    if request.user.is_authenticated:
        try:
            # First, try to get from UserProfile
            sede = request.user.profile.sede
        except UserProfile.DoesNotExist:
            try:
                # Fallback to the direct OneToOneField on Sede
                sede = request.user.sede
            except Sede.DoesNotExist:
                sede = None # No sede associated with this user


    return render(request, 'admin/admin_players.html', {
        'current_song': current_song,
        'playlist': playlist,
        'songs_json': json.dumps(songs_list),
        'sede': sede,
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

@csrf_exempt
@require_POST
def update_sede_status(request):
    """
    Endpoint para actualizar el estado de una sede a 'activo' o 'inactivo'.
    """
    print("DEBUG: update_sede_status view reached.")
    try:
        data = json.loads(request.body.decode('utf-8'))
        sede_id = data.get('sede_id')
        status = data.get('status')
        print(f"DEBUG: Received sede_id: {sede_id}, status: {status}")

        if not sede_id or not status:
            return JsonResponse({'status': 'error', 'message': 'Faltan sede_id o status'}, status=400)

        if status not in ['activo', 'inactivo']:
            return JsonResponse({'status': 'error', 'message': 'El estado debe ser "activo" o "inactivo"'}, status=400)

        sede = get_object_or_404(Sede, id=sede_id)
        sede.estado = status
        sede.save(update_fields=['estado'])
        
        print(f"DEBUG: Successfully updated Sede '{sede.nombre}' to '{status}'.")
        return JsonResponse({'status': 'success', 'message': f'Estado de la sede {sede.nombre} actualizado a {status}.'})

    except json.JSONDecodeError:
        print("DEBUG: Error decoding JSON.")
        return JsonResponse({'status': 'error', 'message': 'Cuerpo de petición JSON inválido.'}, status=400)
    except Sede.DoesNotExist:
        print(f"DEBUG: Sede with ID {sede_id} not found.")
        return JsonResponse({'status': 'error', 'message': f'Sede con ID {sede_id} no encontrada.'}, status=404)
    except Exception as e:
        print(f"DEBUG: An unexpected error occurred: {e}")
        logging.error(f"Error al actualizar estado de la sede: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)