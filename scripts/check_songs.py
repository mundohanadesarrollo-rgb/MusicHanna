import os
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.admin.models import Song
from django.conf import settings
import os as _os

print('MEDIA_ROOT:', settings.MEDIA_ROOT)
for s in Song.objects.all():
    print('Song', s.id, s.titulo)
    audio_name = getattr(s, 'archivo_audio').name if getattr(s, 'archivo_audio', None) else None
    print(' audio name:', audio_name)
    path = None
    try:
        path = s.archivo_audio.path
    except Exception as e:
        path = None
    print(' archivo path:', path)
    if path:
        print(' exists:', _os.path.exists(path))
    print(' url:', getattr(s, 'archivo_audio').url if getattr(s, 'archivo_audio', None) else None)
    print('---')
