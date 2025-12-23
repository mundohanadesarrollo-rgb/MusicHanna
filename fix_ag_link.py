import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import Sede, UserProfile
from django.contrib.auth.models import User

def fix_ag_01():
    print("--- REPARANDO VINCULACIÓN DE AG-01 ---")
    try:
        user = User.objects.get(username='AG-01')
        print(f"Usuario AG-01 encontrado (ID: {user.id})")
        
        # Buscar sede que debería ser de AG-01
        sede = Sede.objects.filter(nombre__icontains='01').first()
        if not sede:
            sede = Sede.objects.create(nombre='Agencia 01', estado='inactivo')
            print("Sede 'Agencia 01' creada desde cero.")
        
        print(f"Sede identificada: {sede.nombre} (ID: {sede.id})")
        
        # 1. Vincular en el modelo Sede
        sede.usuario = user
        sede.save()
        print("Model Sede: Campo 'usuario' actualizado.")
        
        # 2. Vincular en UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.sede = sede
        profile.save()
        print(f"UserProfile: {'Creado y vinculada' if created else 'Actualizada'} con sede ID {sede.id}.")
        
        print("--- REPARACIÓN COMPLETADA ---")
        
    except User.DoesNotExist:
        print("ERROR: El usuario AG-01 no existe en la base de datos.")

if __name__ == "__main__":
    fix_ag_01()
