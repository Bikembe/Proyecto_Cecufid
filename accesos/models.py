from django.db import models
from django.utils import timezone


class Acceso(models.Model):

    nadador = models.ForeignKey(
        'usuarios.Nadador',
        on_delete=models.CASCADE
    )

    fecha = models.DateTimeField(default=timezone.now)

    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='ENTRADA'
    )

    def __str__(self):
        return f"{self.nadador} - {self.tipo} - {self.fecha}"