import os
import django
from django.test import RequestFactory
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.views import user_dashboard

def test_dashboard_context(username):
    user = User.objects.get(username=username)
    rf = RequestFactory()
    request = rf.get('/users/dashboard/')
    request.user = user
    
    # We call the view but need to catch the context
    # Instead of calling view, let's replicate logic
    sede_name = None
    profile = getattr(user, 'profile', None)
    sede = None
    if profile is not None:
        sede = getattr(profile, 'sede', None)
    if not sede:
        try:
            sede = user.sede
        except Exception:
            sede = None
            
    print(f"User: {username}")
    print(f"Profile: {profile}")
    print(f"Sede: {sede}")
    if sede:
        print(f"Sede ID: {sede.id}")

test_dashboard_context('AG-01')
test_dashboard_context('admin')
