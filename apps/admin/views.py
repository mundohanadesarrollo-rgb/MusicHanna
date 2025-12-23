from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Create your views here.

def format_duration(seconds):
    return str(datetime.timedelta(seconds=int(seconds)))

@login_required
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
            'author': 'MusicHanna Admin',
            'status': sede.estado,
            'image': 'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=200&q=80',
        })

    sedes_totales = len(actividad_reciente)
    nuevos_registros = len(subidas_revision)

    # Get the sede for the player.
    current_sede = None
    if request.user.is_authenticated:
        try:
            current_sede = request.user.profile.sede
        except (UserProfile.DoesNotExist, Sede.DoesNotExist, AttributeError):
             try:
                current_sede = request.user.sede
             except (Sede.DoesNotExist, AttributeError):
                current_sede = None

    if not current_sede:
        current_sede = Sede.objects.first()

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

@login_required
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

        usuario_username = s.usuario.username if getattr(s, 'usuario', None) else ''
        usuario_id = s.usuario.id if getattr(s, 'usuario', None) else None

        sedes.append({
            'id': s.id,
            'nombre': s.nombre,
            'estado': estado_display,
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

@login_required
def admin_edit_sede(request, sede_id=None):
    if sede_id:
        sede = get_object_or_404(Sede, id=sede_id)
    else:
        sede = None

    from .forms import SedeForm

    if request.method == 'POST':
        form = SedeForm(request.POST, instance=sede)
        if form.is_valid():
            instance = form.save(commit=False)
            new_username = form.cleaned_data.get('new_username')
            new_password = form.cleaned_data.get('new_password')
            usuario_display = form.cleaned_data.get('usuario_display')
            usuario_id = request.POST.get('usuario') 

            if new_username:
                if User.objects.filter(username=new_username).exists():
                    form.add_error('new_username', 'El nombre de usuario ya existe.')
                else:
                    user = User.objects.create_user(username=new_username, password=new_password)
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()
                    instance.usuario = user
            elif not usuario_id and usuario_display and sede and sede.usuario:
                original_username = sede.usuario.username
                if usuario_display != original_username:
                    if User.objects.filter(username=usuario_display).exclude(pk=sede.usuario.pk).exists():
                        form.add_error('usuario_display', f'El nombre de usuario "{usuario_display}" ya existe.')
                    else:
                        sede.usuario.username = usuario_display
                        sede.usuario.save(update_fields=['username'])
                        instance.usuario = sede.usuario
                else:
                    instance.usuario = sede.usuario
            else:
                usuario = form.cleaned_data.get('usuario')
                if usuario:
                    instance.usuario = usuario
                else:
                    if sede and not usuario_display:
                        instance.usuario = None

            if form.errors:
                 if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
                    return JsonResponse({'success': False, 'errors': errors}, status=400)

            instance.save()
            assigned_username = instance.usuario.username if getattr(instance, 'usuario', None) else None
            
            if assigned_username:
                messages.success(request, f'Sede guardada correctamente. Usuario asignado: {assigned_username}')
            else:
                messages.success(request, 'Sede guardada correctamente. (Sin usuario asignado)')

            try:
                assigned_user = instance.usuario
                if assigned_user:
                    UserProfile.objects.update_or_create(user=assigned_user, defaults={'sede': instance})
            except Exception:
                pass

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('admin_sedes')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = SedeForm(instance=sede)

    return render(request, 'admin/edit_sede.html', {'form': form, 'sede': sede})

@login_required
def admin_delete_sede(request, sede_id):
    if request.method == 'POST':
        try:
            sede = get_object_or_404(Sede, id=sede_id)
            sede_nombre = sede.nombre 
            user_to_delete = getattr(sede, 'usuario', None)
            sede.delete()
            if user_to_delete:
                user_to_delete_username = user_to_delete.username
                user_to_delete.delete()
                messages.success(request, f'Sede "{sede_nombre}" y usuario "{user_to_delete_username}" eliminados correctamente.')
            else:
                messages.success(request, f'Sede "{sede_nombre}" eliminada correctamente. No había usuario asociado.')
        except Exception as e:
             messages.error(request, f'Ocurrió un error al intentar eliminar la sede: {e}')
    return redirect('admin_sedes')

@login_required
@csrf_exempt
@require_POST
def play_signal(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        sede_id = data.get('sede_id')
        song_id = data.get('song_id')
        if not sede_id or not song_id:
            return JsonResponse({'status': 'error', 'message': 'Faltan sede_id o song_id'}, status=400)
        sede = Sede.objects.get(id=sede_id)
        song = Song.objects.get(id=song_id)
        user = getattr(sede, 'usuario', None)
        Play.objects.create(cancion=song, sede=sede, usuario=user)
        sede.estado = 'activo'
        sede.save() 
        print(f"DEBUG play_signal: Sede {sede.nombre} (ID {sede.id}) set to ACTIVO")
        return JsonResponse({'status': 'success', 'message': 'Reproducción registrada y sede activada.'})
    except Exception as e:
        print(f"DEBUG ERROR play_signal: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@csrf_exempt
@require_POST
def stop_signal(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        sede_id = data.get('sede_id')
        if not sede_id:
            return JsonResponse({'status': 'error', 'message': 'Falta sede_id'}, status=400)
        sede = Sede.objects.get(id=sede_id)
        sede.estado = 'inactivo'
        sede.save()
        print(f"DEBUG stop_signal: Sede {sede.nombre} (ID {sede.id}) set to INACTIVO")
        return JsonResponse({'status': 'success', 'message': 'Sede marcada como inactiva.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def admin_uploads(request):
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            artist_name = form.cleaned_data['artist_name']
            artist, _ = Artist.objects.get_or_create(nombre=artist_name)
            album_title = form.cleaned_data['album_title']
            album = None
            if album_title:
                album, _ = Album.objects.get_or_create(titulo=album_title, artista=artist)
            song = form.save(commit=False)
            song.artista = artist
            song.album = album
            audio_file = request.FILES['archivo_audio']
            try:
                audio = MP3(audio_file)
                song.duracion = datetime.timedelta(seconds=int(audio.info.length))
            except Exception:
                song.duracion = datetime.timedelta(seconds=0)
            song.save()
            messages.success(request, f"La canción '{song.titulo}' ha sido subida con éxito.")
            return redirect('admin_uploads')
        else:
            messages.error(request, "No se pudo subir la canción.")
            uploads = Song.objects.select_related('artista', 'album').all()
            return render(request, 'admin/admin_uploads.html', {'uploads': uploads, 'form': form})
    else:
        form = SongForm()
    uploads = Song.objects.select_related('artista', 'album').all()
    return render(request, 'admin/admin_uploads.html', {'uploads': uploads, 'form': form})

@login_required
def admin_players(request, song_id=None):
    all_songs = Song.objects.select_related('artista', 'album').all().order_by('-fecha_subida')
    if not all_songs.exists():
        return render(request, 'admin/admin_players.html', {'current_song': None})
    current_song = all_songs.filter(id=song_id).first() if song_id else all_songs.first()
    if not current_song:
        current_song = all_songs.first()
    if not getattr(current_song, 'archivo_audio', None):
        song_with_audio = all_songs.filter(archivo_audio__isnull=False).exclude(id=current_song.id).first()
        if song_with_audio:
            current_song = song_with_audio
    playlist = all_songs.exclude(id=current_song.id)
    songs_for_js = sorted(all_songs, key=lambda x: x.id != current_song.id)
    valid_songs_for_js = []
    for s in songs_for_js:
        try:
            has_audio = bool(s.archivo_audio and (hasattr(s.archivo_audio, 'path') and s.archivo_audio.storage.exists(s.archivo_audio.name)))
        except Exception:
            try:
                has_audio = bool(s.archivo_audio and s.archivo_audio.path and os.path.exists(s.archivo_audio.path))
            except Exception:
                has_audio = False
        if has_audio:
            valid_songs_for_js.append(s)
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
            sede = request.user.profile.sede
        except Exception:
            try:
                sede = request.user.sede
            except Exception:
                sede = None
        if sede and sede.estado != 'inactivo':
             sede.estado = 'inactivo'
             sede.save()
    return render(request, 'admin/admin_players.html', {
        'current_song': current_song,
        'playlist': playlist,
        'songs_json': json.dumps(songs_list),
        'sede': sede,
    })

@login_required
def admin_delete_song(request, song_id):
    if request.method == 'POST':
        song = get_object_or_404(Song, id=song_id)
        if song.archivo_audio and hasattr(song.archivo_audio, 'path'):
            try:
                song.archivo_audio.delete(save=False)
            except Exception: pass
        if song.imagen and hasattr(song.imagen, 'path'):
            try:
                song.imagen.delete(save=False)
            except Exception: pass
        song.delete()
        messages.success(request, f"La canción '{song.titulo}' ha sido eliminada con éxito.")
    return redirect('admin_uploads')

def admin_login(request):
    return render(request, 'admin/login.html')

def admin_logout(request):
    logout(request)
    return redirect('user_login')

@login_required
@csrf_exempt
@require_POST
def update_sede_status(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        sede_id = data.get('sede_id')
        status = data.get('status')
        if not sede_id or not status:
            return JsonResponse({'status': 'error', 'message': 'Faltan sede_id o status'}, status=400)
        if status not in ['activo', 'inactivo']:
            return JsonResponse({'status': 'error', 'message': 'El estado debe ser "activo" o "inactivo"'}, status=400)
        sede = get_object_or_404(Sede, id=sede_id)
        sede.estado = status
        sede.save() 
        print(f"DEBUG update_sede_status: Sede {sede.nombre} (ID {sede.id}) set to {status.upper()}")
        return JsonResponse({'status': 'success', 'message': f'Estado de la sede {sede.nombre} actualizado a {status}.'})
    except Exception as e:
        print(f"DEBUG ERROR update_sede_status: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def get_sedes_status(request):
    sedes = Sede.objects.all()
    timeout_threshold = timezone.timedelta(seconds=45) 
    now = timezone.now()
    data = []
    for s in sedes:
        if s.estado == 'activo' and s.ultima_actualizacion:
            if now - s.ultima_actualizacion > timeout_threshold:
                s.estado = 'inactivo'
                s.save()
        is_active = (s.estado == 'activo')
        if is_active:
             badge_class = 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-200 text-green-800 dark:bg-green-900 dark:text-green-200'
             dot_class = 'w-2 h-2 rounded-full bg-green-500'
             estado_display = 'Activo'
        else:
             badge_class = 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-200 text-red-800 dark:bg-red-900 dark:text-red-200'
             dot_class = 'w-2 h-2 rounded-full bg-red-500'
             estado_display = 'Inactivo'
        data.append({
            'id': s.id,
            'estado': estado_display,
            'badge_class': badge_class,
            'dot_class': dot_class
        })
    return JsonResponse({'sedes': data})
