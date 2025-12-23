import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile, Sede

def analyze_user(username):
    print(f"\n--- ANALIZANDO USUARIO: {username} ---")
    try:
        user = User.objects.get(username=username)
        print(f"User ID: {user.id}")
        
        # 1. Check UserProfile
        profile = getattr(user, 'profile', None)
        print(f"Has Profile: {profile is not None}")
        if profile:
            print(f"Profile Sede: {profile.sede}")
        
        # 2. Check Reverse Sede relation
        try:
            rev_sede = user.sede
            print(f"Reverse Sede (user.sede): {rev_sede} (ID: {rev_sede.id})")
        except Exception as e:
            print(f"Reverse Sede Error: {e}")
            
        # 3. Check Sedes where usuario=user
        sedes_linked = Sede.objects.filter(usuario=user)
        print(f"Sedes where usuario=user: {list(sedes_linked)}")

    except User.DoesNotExist:
        print("User not found")

analyze_user('AG-01')
analyze_user('admin')
