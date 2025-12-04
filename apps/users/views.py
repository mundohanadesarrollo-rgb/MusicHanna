from django.shortcuts import render, redirect
from django.contrib.auth import logout
from apps.admin.models import Song, Play
def user_logout(request):
    logout(request)
    return redirect('user_login')

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
            # `sede` puede ser una instancia del modelo o un valor; obtener nombre seguro
            sede_name = getattr(sede, 'nombre', None) or str(sede)

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
        'sede_name': sede_name,
        'recent_songs': recent_songs,
        'playlist_songs': playlist_songs,
    }

    return render(request, 'users/user_dashboard.html', context)