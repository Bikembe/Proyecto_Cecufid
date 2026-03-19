from django.db import models
from usuarios.models import Inscripcion
from asignaciones.models import HorarioCarril


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
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    fecha = models.DateField()
    asistio = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
