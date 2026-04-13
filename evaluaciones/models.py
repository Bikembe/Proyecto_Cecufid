from django.db import models


class Evaluacion(models.Model):

    nadador = models.ForeignKey(
        'usuarios.Nadador',
        on_delete=models.CASCADE,
        related_name='evaluaciones_tecnicas'
    )

    horario_carril = models.ForeignKey(
        'asignaciones.HorarioCarril',
        on_delete=models.CASCADE,
        related_name='evaluaciones_tecnicas'
    )

    maestro = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_realizadas'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    respiracion = models.IntegerField(default=0)
    libre = models.IntegerField(default=0)
    espalda = models.IntegerField(default=0)
    mariposa = models.IntegerField(default=0)
    resistencia = models.IntegerField(default=0)

    promedio = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    observaciones = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):

        valores = [
            int(self.respiracion or 0),
            int(self.libre or 0),
            int(self.espalda or 0),
            int(self.mariposa or 0),
            int(self.resistencia or 0),
        ]

        self.promedio = round(sum(valores) / len(valores), 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nadador} - {self.promedio}"