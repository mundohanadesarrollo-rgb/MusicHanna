
@login_required
def get_sedes_status(request):
    """
    Retorna el estado actual de todas las sedes en formato JSON.
    """
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
