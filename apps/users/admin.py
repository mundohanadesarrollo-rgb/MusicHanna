from django.contrib import admin
from .models import Sede, UserProfile

# Register your models here.


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado', 'ciudad', 'pais', 'ultima_actualizacion')
    list_filter = ('estado', 'ciudad', 'pais')
    search_fields = ('nombre', 'ciudad', 'direccion')
    ordering = ('nombre',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'sede', 'fecha_creacion')
    list_filter = ('sede',)
    search_fields = ('user__username', 'user__email', 'biografia')
    raw_id_fields = ('user',)
