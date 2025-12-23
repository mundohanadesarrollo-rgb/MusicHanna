import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import Sede
from django.contrib.auth.models import User

print("--- USUARIOS Y SEDES ---")
users = User.objects.all()
for u in users:
    sede = getattr(u, 'sede', None)
    print(f"User: {u.username} (ID: {u.id}) | Sede: {sede.nombre if sede else 'None'} (Sede ID: {sede.id if sede else 'N/A'})")
print("-------------------------")
