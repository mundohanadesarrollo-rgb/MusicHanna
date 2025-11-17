from django.shortcuts import render

# Create your views here.

def admin_dashboard(request):
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
