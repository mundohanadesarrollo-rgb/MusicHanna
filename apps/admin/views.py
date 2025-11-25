from django.shortcuts import render

# Create your views here.

def admin_dashboard(request):
    subidas_revision = [
        {
            'id': 1,
            'name': 'Echoes in Silence',
            'author': 'Liam Harper',
            'fecha_subida': '2024-06-10',
            'image': 'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=200&q=80',
        },
        {
            'id': 2,
            'name': 'Velvet Horizons',
            'author': 'Isabella Reyes',
            'fecha_subida': '2024-06-11',
            'image': 'https://images.unsplash.com/photo-1501612780327-45045538702b?auto=format&fit=crop&w=200&q=80',
        },
        
    ]

    actividad_reciente = [
        {
            'nro_sede': 1,
            'name': 'Bohemian Rhapsody',
            'author': 'Queen',
            'status': 'activo',
            'image': 'https://images.unsplash.com/photo-1485579149621-3123dd979885?auto=format&fit=crop&w=200&q=80',
        },
        {
            'nro_sede': 2,
            'name': 'Stairway to Heaven',
            'author': 'Led Zeppelin',
            'status': 'inactivo',
            'image': 'https://images.unsplash.com/photo-1507878866276-a947ef722fee?auto=format&fit=crop&w=200&q=80',
        },
    ]

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
    return render(request, 'admin/admin_uploads.html')

def admin_players(request):
    return render(request, 'admin/players.html')

def admin_login(request):
    return render(request, 'admin/login.html')

def admin_logout(request):
    return render(request, 'admin/logout.html')
