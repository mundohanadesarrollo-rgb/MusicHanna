import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import Sede
from apps.admin.views import update_sede_status
from django.http import HttpRequest
from django.contrib.auth.models import User

# Mock request
req = HttpRequest()
req.method = 'POST'
req.user = User.objects.get(id=19) # AG-01
req._body = json.dumps({'sede_id': 25, 'status': 'activo'}).encode('utf-8')

print("--- Calling update_sede_status directly ---")
try:
    resp = update_sede_status(req)
    print(f"Status: {resp.status_code}")
    print(f"Content: {resp.content.decode()}")
except Exception as e:
    import traceback
    print(f"FAILED with exception: {e}")
    traceback.print_exc()

# Check DB
sede = Sede.objects.get(id=25)
print(f"Final state in DB: {sede.estado} (Last update: {sede.ultima_actualizacion})")
