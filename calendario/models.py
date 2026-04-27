from django.db import models
from django.conf import settings

from usuarios.models import Inscripcion
from asignaciones.models import HorarioCarril

class CupoRecuperacion(models.Model):

    horario_carril = models.ForeignKey(
        HorarioCarril,
        on_delete=models.CASCADE
    )

    nivel = models.CharField(max_length=50)

    maximo_nadadores = models.PositiveIntegerField(default=5)

    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.horario_carril} - {self.nivel}"

class RecuperacionClase(models.Model):

    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.CASCADE
    )

    horario_carril = models.ForeignKey(
        HorarioCarril,
        on_delete=models.CASCADE
    )

    fecha = models.DateField()

    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    nivel = models.CharField(max_length=50)

    estado = models.CharField(
        max_length=20,
        choices=[
            ('PROGRAMADA', 'Programada'),
            ('CONFIRMADA', 'Confirmada'),
            ('CANCELADA', 'Cancelada')
        ],
        default='PROGRAMADA'
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inscripcion} - {self.fecha}"

class EventoCalendario(models.Model):

    TIPO_EVENTO = [
        ('CANCELACION_DIA', 'Cancelación de día completo'),
        ('CANCELACION_HORARIO', 'Cancelación de horario'),
    ]

    tipo = models.CharField(max_length=30, choices=TIPO_EVENTO)

    horario_carril = models.ForeignKey(
        HorarioCarril,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    fecha = models.DateField()
    cupo_por_horario = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Cupos por horario y nivel SOLO si permite recuperación"
    )
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)

    motivo = models.TextField(blank=True, null=True)
    permite_recuperacion = models.BooleanField(default=False)

    fechas_recuperacion = models.JSONField(
        null=True,
        blank=True
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.fecha}"

class Horario(models.Model):

    horario_carril = models.ForeignKey(
        HorarioCarril,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    dia_semana = models.CharField(max_length=20)

    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Asistencia(models.Model):

    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.CASCADE
    )

    fecha = models.DateField()

    asistio = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
