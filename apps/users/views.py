from django.shortcuts import render, redirect
from django.contrib.auth import logout


def user_logout(request):
    logout(request)
    return redirect('user_login')

def user_dashboard(request):
    usuario ={
        'sede': 'Sede Central',
    }
    return render(request, 'users/user_dashboard.html',
                  {
                      'usuario': usuario
                  })