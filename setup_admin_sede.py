import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import Sede, UserProfile
from django.contrib.auth.models import User

def setup_admin_sede():
    admin_user = User.objects.get(username='admin')
    
    # Check if sede exists
    sede_name = "Agencia 00"
    sede, created = Sede.objects.get_or_create(
        nombre=sede_name,
        defaults={'estado': 'inactivo', 'ciudad': 'Administración', 'direccion': 'Sede Principal'}
    )
    
    if created:
        print(f"Sede '{sede_name}' creada.")
    else:
        print(f"Sede '{sede_name}' ya existe.")

    # Assign user to Sede
    sede.usuario = admin_user
    sede.save()
    print(f"Usuario 'admin' asignado como responsable de la sede '{sede_name}'.")

    # Update UserProfile if exists or create it
    profile, p_created = UserProfile.objects.update_or_create(
        user=admin_user,
        defaults={'sede': sede}
    )
    print(f"Perfil de 'admin' actualizado con la sede '{sede_name}'.")

if __name__ == "__main__":
    setup_admin_sede()
