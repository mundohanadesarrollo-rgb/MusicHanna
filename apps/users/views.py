from django.shortcuts import render

# Create your views here.

def user_login(request):
    return render(request, 'users/user_login.html')

def user_logout(request):
    return render(request, 'users/user_logout.html')

def user_dashboard(request):
    return render(request, 'users/user_dashboard.html')