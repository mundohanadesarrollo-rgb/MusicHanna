from django.shortcuts import render

# Create your views here.

def admin_dashboard(request):
    subidas_revision = [
        {
            'id': 1,
            'name': 'Echoes in Silence',
            'author': 'Liam Harper',
            'date_uploaded': '2024-06-10',
            'image': 'https://…',
            'status': 'Pending Review',
        },
    ]

    actividad_reciente = [
        {
            'nro_sede': 1,
            'name': 'Bohemian Rhapsody',
            'author': 'Queen',
            'status': 'activo',
        },
        {
            'nro_sede': 2,
            'name': 'Stairway to Heaven',
            'author': 'Led Zeppelin',
            'status': 'inactivo',
        },
    ]

    return render(
        request,
        'admin/dashboard.html',
        {
            'subidas_revision': subidas_revision,
            'actividad_reciente': actividad_reciente,
        },
    )

def admin_sedes(request):
    return render(request, 'admin/admin_sedes.html')

def admin_uploads(request):
    return render(request, 'admin/uploads.html')

def admin_players(request):
    return render(request, 'admin/players.html')

def admin_login(request):
    return render(request, 'admin/login.html')

def admin_logout(request):
    return render(request, 'admin/logout.html')
