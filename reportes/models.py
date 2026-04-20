from django.db import models
from django.utils import timezone
from datetime import timedelta
from usuarios.models import Usuario


class HistorialAccion(models.Model):

    class Modulos(models.TextChoices):
        USUARIOS = 'USUARIOS', 'Usuarios'
        PLANES = 'PLANES', 'Planes'
        REPORTES = 'REPORTES', 'Reportes'
        SISTEMA = 'SISTEMA', 'Sistema'
        OTRO = 'OTRO', 'Otro'

    class TipoAccion(models.TextChoices):
        CREAR = 'CREAR', 'Crear'
        EDITAR = 'EDITAR', 'Editar'
        ELIMINAR = 'ELIMINAR', 'Eliminar'
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        CONSULTA = 'CONSULTA', 'Consulta'

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='historial_acciones',
        db_index=True
    )

    modulo = models.CharField(
        max_length=20,
        choices=Modulos.choices,
        db_index=True
    )

    accion = models.CharField(
        max_length=20,
        choices=TipoAccion.choices,
        db_index=True
    )

    descripcion = models.TextField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    user_agent = models.TextField(blank=True, null=True)

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['usuario', 'fecha']),
            models.Index(fields=['modulo', 'fecha']),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.modulo}"


class UsuarioActivo(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='activo'
    )

    ultima_actividad = models.DateTimeField(db_index=True)

    conectado = models.BooleanField(default=False)

    def esta_en_linea(self):
        return self.ultima_actividad >= timezone.now() - timedelta(minutes=5)

    def __str__(self):
        return self.usuario.username


class Reporte(models.Model):

    class TipoReporte(models.TextChoices):
        USUARIOS = 'USUARIOS', 'Usuarios'
        ACTIVIDAD = 'ACTIVIDAD', 'Actividad'
        FINANCIERO = 'FINANCIERO', 'Financiero'
        PERSONALIZADO = 'PERSONALIZADO', 'Personalizado'

    titulo = models.CharField(
    max_length=150,
    default="Reporte sin título"
)

    tipo = models.CharField(
    max_length=20,
    choices=TipoReporte.choices,
    db_index=True,
    default=TipoReporte.PERSONALIZADO
)

    descripcion = models.TextField(blank=True, null=True)

    generado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes_generados'
    )

    parametros = models.JSONField(blank=True, null=True)

    archivo = models.FileField(upload_to='reportes/', blank=True, null=True)

    fecha_generacion = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-fecha_generacion']

    def __str__(self):
        return self.titulo