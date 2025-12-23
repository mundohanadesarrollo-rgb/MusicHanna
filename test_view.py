import os
import django
import json
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import Sede

# Create a test client
c = Client()

# Get the AG-01 user (ID 19)
user = User.objects.get(id=19)
c.force_login(user)

# Try to update status
print("--- TEST: Manual status update via Client ---")
response = c.post('/admin/update_sede_status/', 
                 data=json.dumps({'sede_id': 25, 'status': 'activo'}), 
                 content_type='application/json')

print(f"Server Status Code: {response.status_code}")
print(f"Server Response: {response.content.decode()}")

# Verify in DB
sede = Sede.objects.get(id=25)
print(f"Sede ID 25 state after test: {sede.estado}")
print(f"Sede ID 25 updated at: {sede.ultima_actualizacion}")
print("---------------------------------------------")
