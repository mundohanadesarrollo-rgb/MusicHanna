from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('bitacora/', views.admin_sedes, name='admin_sedes'),
    path('uploads/', views.admin_uploads, name='admin_uploads'),
    path('players/', views.admin_players, name='admin_players'),
    path('players/<int:song_id>/', views.admin_players, name='admin_player_song'),
    path('uploads/delete/<int:song_id>/', views.admin_delete_song, name='admin_delete_song'),

    path('logout/', views.admin_logout, name='admin_logout'),

]