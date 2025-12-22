
import os

file_path = r'c:\Users\DESARROLLO\Desktop\Proyectos\MusicHanna\apps\admin\views.py'
new_code = """

@login_required
def get_sedes_status(request):
    \"\"\"
    Retorna el estado actual de todas las sedes en formato JSON.
    \"\"\"
    sedes = Sede.objects.all()
    data = []
    for s in sedes:
        is_active = (s.estado == 'activo')
        if is_active:
             badge_class = 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-200 text-green-800 dark:bg-green-900 dark:text-green-200'
             dot_class = 'w-2 h-2 rounded-full bg-green-500'
             estado_display = 'Activo'
        else:
             badge_class = 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-200 text-red-800 dark:bg-red-900 dark:text-red-200'
             dot_class = 'w-2 h-2 rounded-full bg-red-500'
             estado_display = 'Inactivo'
        
        data.append({
            'id': s.id,
            'estado': estado_display,
            'badge_class': badge_class,
            'dot_class': dot_class
        })
    return JsonResponse({'sedes': data})
"""

with open(file_path, 'rb') as f:
    content = f.read()

# Find the end of the valid content
marker = b"return JsonResponse({'status': 'error', 'message': str(e)}, status=500)"
idx = content.rfind(marker)

if idx != -1:
    # Keep up to the end of the marker + newline if present
    # We'll just cut off right after the marker and add a newline
    valid_content = content[:idx + len(marker)]
    
    # decode to string to append new code safely (assuming utf-8 for the valid part)
    # The valid part should be utf-8 compatible
    text_content = valid_content.decode('utf-8')
    
    final_content = text_content + new_code
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("Successfully fixed views.py")
else:
    print("Could not find marker in views.py")
