from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('bitacora/', views.admin_sedes, name='admin_sedes'),
    path('uploads/', views.admin_uploads, name='admin_uploads'),
    path('players/', views.admin_players, name='admin_players'),
    path('players/<int:song_id>/', views.admin_players, name='admin_player_song'),
    path('uploads/delete/<int:song_id>/', views.admin_delete_song, name='admin_delete_song'),
    path('sedes/edit/<int:sede_id>/', views.admin_edit_sede, name='admin_edit_sede'),
    path('sedes/add/', views.admin_edit_sede, name='admin_add_sede'),
    path('sedes/delete/<int:sede_id>/', views.admin_delete_sede, name='admin_delete_sede'),
    path('update_sede_status/', views.update_sede_status, name='update_sede_status'),

    path('play_signal/', views.play_signal, name='play_signal'),
    path('stop_signal/', views.stop_signal, name='stop_signal'),
    path('sedes/status/', views.get_sedes_status, name='get_sedes_status'),
    path('logout/', views.admin_logout, name='admin_logout'),
]