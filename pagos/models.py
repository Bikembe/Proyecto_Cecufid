from django.db import models


class Pago(models.Model):

    TIPO_PAGO = (
        ('EXAMEN', 'Examen Médico'),
        ('INSCRIPCION', 'Inscripción'),
        ('MENSUALIDAD', 'Mensualidad'),
    )

    ESTADO_PAGO = (
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
    )

    preregistro = models.ForeignKey(
        "preregistro.PreRegistro",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pagos"
    )

    inscripcion = models.ForeignKey(
        "usuarios.Inscripcion",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pagos"
    )

    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO)

    monto = models.DecimalField(max_digits=8, decimal_places=2)

    metodo_pago = models.CharField(max_length=50)

    fecha_pago = models.DateField(auto_now_add=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO,
        default='PAGADO'
    )

    referencia = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.preregistro and not self.inscripcion:
            raise ValidationError("Debe tener preregistro o inscripción")

        if self.preregistro and self.inscripcion:
            raise ValidationError("Solo puede tener preregistro o inscripción, no ambos")

    def __str__(self):
        if self.preregistro:
            return f"Pago {self.tipo_pago} - PR {self.preregistro.folio}"
        return f"Pago {self.tipo_pago} - INS {self.inscripcion.id}"

class Descuento(models.Model):
    nombre = models.CharField(max_length=100)
    porcentaje = models.IntegerField()  # 50 = 50%
    requiere_credencial = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} - {self.porcentaje}%"

class Tarifa(models.Model):

    TIPO = (
        ('INSCRIPCION', 'Inscripción'),
        ('EXAMEN', 'Examen Médico'),
        ('MENSUALIDAD', 'Mensualidad'),
    )

    DIAS_OPCIONES = (
        (1, '1 día'),
        (2, '2 días'),
        (3, '3 días'),
        (5, '5 días'),
    )

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO)

    dias = models.IntegerField(choices=DIAS_OPCIONES, null=True, blank=True)

    monto = models.DecimalField(max_digits=8, decimal_places=2)

    activo = models.BooleanField(default=True)

    def __str__(self):
        if self.tipo == "MENSUALIDAD":
            return f"{self.nombre} ({self.dias} días) - ${self.monto}"
        return f"{self.nombre} - ${self.monto}"