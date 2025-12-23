import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import Sede

sedes = Sede.objects.all()
print("--- ESTADO DE LAS SEDES EN DB ---")
for s in sedes:
    print(f"ID: {s.id} | Sede: {s.nombre} | Estado: {s.estado} | Last Update: {s.ultima_actualizacion}")
print("---------------------------------")
