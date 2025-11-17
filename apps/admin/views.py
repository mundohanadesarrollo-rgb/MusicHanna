from django.shortcuts import render

# Create your views here.

def admin_dashboard(request):

    subidas_revision = [
        {
        'id': 1,
        'name': 'Echoes in Silence',
        'author': 'Liam Harper',
        'date_uploaded': '2024-06-10',
        'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuAgNsMR0vB1MZAgv7lZ3cuhksKupZ6y_su_R6rPd64137U4VtkPeUvKXejpFrlQDHgbgQYtx9rwFPWfDF1FxgkDeprtzL06DAJBUJ99zP-TN1wOehxggPr4TZQk6N-Rmj3BL1QJkrie7_WpTE5YYURg0GukWDEb3scdjcPBNH95ZRT_CvCOM_Mvb3wWoCn4RWmujg033w-rvn7maJ2z50iudmgbMWRFOfIJt_cnvVyOYPvDHO1zY2bJQYxfKoZLo-SseWGWlHVDiea8',
        'status': 'Pending Review',
        },

    ],

    actividad_reciente = [
        {
            'nro_sede': 1,
            'name': 'bohemian rhapsody',
            'author': 'queen',
            'status': 'activo',

            'nro_sede': 2,
            'name': 'stairway to heaven',
            'author': 'led zeppelin',
            'status': 'inactivo',



        }
        
        ]


    return render(request, 'admin/dashboard.html')

def admin_users(request):
    return render(request, 'admin/users.html')

def admin_uploads(request):
    return render(request, 'admin/uploads.html')

def admin_players(request):
    return render(request, 'admin/players.html')

def admin_login(request):
    return render(request, 'admin/login.html')

def admin_logout(request):
    return render(request, 'admin/logout.html')
