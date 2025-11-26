from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def user_login(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        contrasena = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=contrasena)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    
    return render(request, 'users/user_login.html')

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