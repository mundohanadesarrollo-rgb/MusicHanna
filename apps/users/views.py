from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from apps.admin.models import Song, Play
def user_logout(request):
    logout(request)
    return redirect('user_login')

@login_required
def user_dashboard(request):
    """Renderiza el dashboard del usuario e incluye el nombre de la sede.

    Intenta obtener la sede desde `request.user.profile.sede` y, si no existe,
    desde la relación inversa `request.user.sede` definida en el modelo `Sede`.
    Pasa `sede_name` a la plantilla (o `None` si no se encuentra).
    """
    sede_name = None
    user = request.user

    if user and user.is_authenticated:
        # Intentar por perfil extendido primero
        profile = getattr(user, 'profile', None)
        sede = None
        if profile is not None:
            sede = getattr(profile, 'sede', None)

        # Si no hay sede en el profile, intentar la relación inversa `user.sede`
        if not sede:
            sede = getattr(user, 'sede', None)

        if sede:
            # Asegurar que sea la instancia del modelo y no un RelatedManager
            if hasattr(sede, 'first'): # Por si acaso es un queryset
                sede = sede.first()
            
            if sede:
                sede_name = getattr(sede, 'nombre', None) or str(sede)
                print(f"DEBUG: Dashboard user {user.username} - Sede: {sede_name} (ID: {sede.id})")
                
                # Resetear estado a 'inactivo' al entrar al dashboard
                if hasattr(sede, 'estado') and sede.estado != 'inactivo':
                    sede.estado = 'inactivo'
                    sede.save()
            else:
                print(f"DEBUG: Dashboard user {user.username} - NO SEDE AFTER RESOLVE")
        else:
            print(f"DEBUG: Dashboard user {user.username} - NO SEDE FOUND")

    # Obtener canciones reproducidas recientemente (únicas, en orden descendente por fecha)
    recent_songs = []
    try:
        plays_qs = Play.objects.all().select_related('cancion', 'cancion__artista')
        if sede:
            plays_qs = plays_qs.filter(sede=sede)
        plays_qs = plays_qs.order_by('-fecha_hora')[:50]

        seen = set()
        for p in plays_qs:
            s = p.cancion
            if s and s.id not in seen:
                recent_songs.append(s)
                seen.add(s.id)
                if len(recent_songs) >= 12:
                    break
    except Exception:
        recent_songs = []

    # Playlist general: incluir todas las canciones de la base de datos
    try:
        playlist_songs = Song.objects.all().select_related('artista')[:200]
    except Exception:
        playlist_songs = []

    context = {
        'sede': sede,
        'sede_id': sede.id if sede else None,
        'sede_name': sede_name,
        'recent_songs': recent_songs,
        'playlist_songs': playlist_songs,
    }

    return render(request, 'users/user_dashboard.html', context)