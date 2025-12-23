import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def create_or_update_admin():
    username = 'admin'
    password = 'password'
    
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"Usuario '{username}' ya existía. Contraseña actualizada y privilegios de administrador asegurados.")
    except User.DoesNotExist:
        user = User.objects.create_superuser(username=username, password=password, email='admin@example.com')
        print(f"Superusuario '{username}' creado exitosamente con la contraseña proporcionada.")

if __name__ == "__main__":
    create_or_update_admin()
