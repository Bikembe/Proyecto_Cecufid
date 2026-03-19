from django.db import models
from usuarios.models import Nadador

class EvaluacionMedica(models.Model):
    nadador = models.ForeignKey(Nadador, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    estatura = models.DecimalField(max_digits=4, decimal_places=2)
    presion_arterial = models.CharField(max_length=20)
    frecuencia_cardiaca = models.IntegerField()
    diagnostico = models.TextField()
    apto = models.BooleanField()
    observaciones = models.TextField(blank=True, null=True)
    fecha_evaluacion = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class EvaluacionDeportiva(models.Model):
    nadador = models.ForeignKey(Nadador, on_delete=models.CASCADE)
    resistencia = models.IntegerField()
    velocidad = models.IntegerField()
    tecnica = models.IntegerField()
    observaciones = models.TextField(blank=True, null=True)
    fecha_evaluacion = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
