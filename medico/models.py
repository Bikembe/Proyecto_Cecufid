from django.db import models
from django.conf import settings
from usuarios.models import Nadador
from usuarios.models import Rol


class Medico(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'rol__nombre': 'Medico'}
    )

    nombre_completo = models.CharField(max_length=200)
    cedula_profesional = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre_completo} - {self.cedula_profesional}"


class CertificadoMedico(models.Model):

    ESTATUS_APTITUD = (
        ('APTO', 'Apto'),
        ('NO_APTO', 'No Apto'),
        ('DIFICULTADES', 'Apto con Dificultades'),
        ('PARANATACION', 'Paranatación'),
    )

    nadador = models.ForeignKey(
        Nadador,
        on_delete=models.CASCADE,
        related_name='certificados'
    )

    medico = models.ForeignKey(
        Medico,
        on_delete=models.PROTECT
    )

    fecha_examen = models.DateTimeField(auto_now_add=True)

    estatus = models.CharField(
        max_length=20,
        choices=ESTATUS_APTITUD
    )

    motivos = models.TextField(blank=True, null=True)

    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    presion_arterial = models.CharField(max_length=20, null=True, blank=True)
    frecuencia_cardiaca = models.IntegerField(null=True, blank=True)
    frecuencia_respiratoria = models.IntegerField(null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    talla = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    imc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    saturacion_oxigeno = models.IntegerField(null=True, blank=True)
    grupo_rh = models.CharField(max_length=10, null=True, blank=True)
    alergias = models.TextField(null=True, blank=True)
    afiliacion = models.CharField(max_length=100, null=True, blank=True)

    conclusion = models.TextField()

    def __str__(self):
        return f"Certificado - {self.nadador} - {self.fecha_examen.date()}"