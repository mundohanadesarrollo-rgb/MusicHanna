import os
import django
from django.template import Context, Template
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import Sede

def test_template_render(username):
    user = User.objects.get(username=username)
    # Replicate view logic
    sede = None
    profile = getattr(user, 'profile', None)
    if profile:
        sede = profile.sede
    if not sede:
        try:
            sede = user.sede
        except:
            sede = None
            
    print(f"--- TESTING TEMPLATE RENDER FOR {username} ---")
    print(f"Internal sede object: {sede}")
    
    template_str = """
    {% if sede %}data-sede-id="{{ sede.id }}"{% else %}NO_SEDE_IN_TEMPLATE{% endif %}
    """
    t = Template(template_str)
    c = Context({'sede': sede})
    rendered = t.render(c).strip()
    print(f"Render result: [{rendered}]")
    print("---------------------------------------------")

test_template_render('AG-01')
test_template_render('admin')
