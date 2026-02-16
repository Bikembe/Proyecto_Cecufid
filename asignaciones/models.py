from django.db import models
from django.core.exceptions import ValidationError


class Nivel(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Carril(models.Model):
    numero = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"Carril {self.numero}"


class HorarioCarril(models.Model):
    carril = models.ForeignKey('Carril', on_delete=models.CASCADE)
    nivel = models.ForeignKey('Nivel', on_delete=models.CASCADE)

    maestro = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        limit_choices_to={'rol__nombre': 'Maestro'}
    )

    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    capacidad_maxima = models.PositiveIntegerField()

    class Meta:
        unique_together = ('carril', 'hora_inicio', 'hora_fin')

    def cupo_ocupado(self):
        return InscripcionCarril.objects.filter(
            horario_carril=self,
            activo=True
        ).count()

    def cupo_disponible(self):
        return self.capacidad_maxima - self.cupo_ocupado()

    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora de fin debe ser mayor que la hora de inicio.")

        traslape = HorarioCarril.objects.filter(
            carril=self.carril,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio
        ).exclude(pk=self.pk)

        if traslape.exists():
            raise ValidationError("Existe traslape de horario en este carril.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.carril} - {self.hora_inicio} a {self.hora_fin} - {self.maestro}"


class InscripcionCarril(models.Model):
    nadador = models.ForeignKey('usuarios.Nadador', on_delete=models.CASCADE)
    horario_carril = models.ForeignKey(
    'HorarioCarril',
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
    fecha = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('nadador', 'horario_carril')

    def clean(self):
        ocupados = InscripcionCarril.objects.filter(
            horario_carril=self.horario_carril,
            activo=True
        ).exclude(pk=self.pk).count()

        if ocupados >= self.horario_carril.capacidad_maxima:
            raise ValidationError("Cupo lleno.")

        traslape = InscripcionCarril.objects.filter(
            nadador=self.nadador,
            activo=True,
            horario_carril__hora_inicio__lt=self.horario_carril.hora_fin,
            horario_carril__hora_fin__gt=self.horario_carril.hora_inicio
        ).exclude(pk=self.pk)

        if traslape.exists():
            raise ValidationError("El nadador ya tiene otro carril en ese horario.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nadador} - {self.horario_carril}"


class Evaluacion(models.Model):
    nadador = models.ForeignKey('usuarios.Nadador', on_delete=models.CASCADE)
    horario_carril = models.ForeignKey('HorarioCarril', on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nadador} - {self.fecha}"


class SolicitudPromocion(models.Model):

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    nadador = models.ForeignKey('usuarios.Nadador', on_delete=models.CASCADE)
    evaluacion = models.ForeignKey('Evaluacion', on_delete=models.CASCADE)

    nivel_actual = models.ForeignKey(
        'Nivel',
        on_delete=models.CASCADE,
        related_name='nivel_actual'
    )

    nivel_sugerido = models.ForeignKey(
        'Nivel',
        on_delete=models.CASCADE,
        related_name='nivel_sugerido'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )

    autorizado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    motivo_rechazo = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nadador} - {self.estado}"