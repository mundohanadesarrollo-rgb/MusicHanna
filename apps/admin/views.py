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
    uploads = [
        {
            'id': 1,
            'title': 'Luces de Neón',
            'artist': 'synthwave_master',
            'album': 'City Nights',
            'duration': '3:45',
            'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDsO49gWiezMp0mvqR5bZRccWHN1dEzFu1e5aIgil9Y7daTEUot2TzgKFUryK7AEEEHhb3EkCi2g8pN8_NCdwAplG628eY9cy7ooofM-FOsn0ha5TaoUijctNpaXe6qiA8V0XsFbjbpzj6MXdgaZ6F2RI4sz6kZu792KDCe-REB3MxvJ2RSwYfOwYNh_iV53y_-cQNNBn43EQX9prlPOD4yQZ5lhZW1T9waS9OzWKvhuFIR9HCyWYce9CSpLd6RQmMPXd7iyvBMHaCa',
            'published': True,
        },
        
    ]
    
    return render(request, 'admin/admin_uploads.html', {
        'uploads': uploads
    })

def admin_players(request):
    players = [
        {
            'id': 1,
            'title': 'Bohemian Rhapsody',
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'duration': '5:55',
            'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDdJSrMKZ15N2XgloMIPnhWWAErOJrQsdRPNxzL1m90sH9qn1IUe2U3CJgfWDzJr_UD35cYGrP7ZTR5r9eBnQHEZenMzAngTEVoA574P1A1_PC1EbBC-0l6t68QmWDmg70THXrQqWUh83e15_x_1bo3zuS_MqemqpYzRvGuGj-afCzO0iyJsbAYjWGDxbLNhESUYcRrdvBzIuHjJUPYjlXnytX-XACBExxYO8kUSQYzS20DWPIOY2y5j01D2JtdKx7u4TLkKdwSe83z',
            'published': True,
            'plays': 1245890,
            'likes': 45230,
            'uploaded_at': '1975-10-31',
        },
        {
            'id': 2,
            'title': 'Stairway to Heaven',
            'artist': 'Led Zeppelin',
            'album': 'Led Zeppelin IV',
            'duration': '8:02',
            'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCUFo-lgwbdiL7DIKFxMoKyPIWkbZ9nrkSGgLvFhbVthT--YpsXfXsTnRnnZlLzohRM29lGWaikEjNE8a7hpIEnYm3sI1aIhopxKwmIl6kWfq3DLAU4yaU0jGiHGV8iHWHHXPqjF8yBhYTwOBXBoX6ULp1vAjGBpZRM7zMG2sOiZ_9sJT_1qZkRE7o-Sv9pRnvsXlwpaOILLkdait6TbFQPekLoaJuOZeoSeseHXUHT0m_xswZgf_uIDJuIUmM5Mj1AwC7NiEVEF50p',
            'published': True,
            'plays': 987654,
            'likes': 38210,
            'uploaded_at': '1971-11-08',
        },
        {
            'id': 3,
            'title': 'Echoes in Silence',
            'artist': 'Liam Harper',
            'album': 'Echoes',
            'duration': '4:15',
            'image': 'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=200&q=80',
            'published': False,
            'plays': 1245,
            'likes': 34,
            'uploaded_at': '2024-06-10',
        },
    ]

    return render(request, 'admin/admin_players.html', 
                  {'players': players}
                  )

def admin_login(request):
    return render(request, 'admin/login.html')

def admin_logout(request):
    return render(request, 'admin/logout.html')
