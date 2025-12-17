from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Sede(models.Model):
    """
    Modelo que representa las sedes o sucursales de MusicHanna.
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Sede")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
        ],
        default='inactivo',
        verbose_name="Estado"
    )
    direccion = models.CharField(max_length=300, blank=True, null=True, verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    pais = models.CharField(max_length=100, default="Colombia", verbose_name="País")
    ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sede',
        verbose_name='Usuario asignado'
    )

    class Meta:
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.estado}"


class UserProfile(models.Model):
    """
    Perfil extendido del usuario que incluye información adicional
    como la sede asignada y foto de perfil.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Usuario"
    )
    sede = models.ForeignKey(
        Sede,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name="Sede Asignada"
    )
    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True,
        verbose_name="Foto de Perfil"
    )
    biografia = models.TextField(blank=True, null=True, verbose_name="Biografía")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"Perfil de {self.user.username}"
