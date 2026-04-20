from django.db import models
from django.utils import timezone
import uuid


class PreRegistro(models.Model):

    ESTADO_CHOICES = (
        ('PENDIENTE_EXAMEN', 'Pendiente examen'),
        ('PAGO_EXAMEN', 'Pago examen'),
        ('APTO', 'Apto'),
        ('NO_APTO', 'No apto'),
        ('PAGO_INSCRIPCION', 'Pago inscripción'),
        ('INSCRITO', 'Inscrito'),
    )

    folio = models.CharField(max_length=20, unique=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE_EXAMEN'
    )

    es_menor = models.BooleanField(default=False)

    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)

    fecha_nacimiento = models.DateField(null=True, blank=True)

    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)

    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True, null=True)

    foto = models.ImageField(upload_to="preregistro/foto/")
    identificacion = models.ImageField(upload_to="preregistro/ine/", blank=True, null=True)

    acta_nacimiento = models.ImageField(upload_to="preregistro/acta/", blank=True, null=True)
    curp_documento = models.ImageField(upload_to="preregistro/curp/", blank=True, null=True)

    nombre_tutor = models.CharField(max_length=200, blank=True, null=True)
    ine_tutor = models.ImageField(upload_to="preregistro/tutor/", blank=True, null=True)
    foto_tutor = models.ImageField(upload_to="preregistro/tutor_foto/", blank=True, null=True)

    categoria = models.ForeignKey(
        "usuarios.Categoria",
        on_delete=models.PROTECT
    )

    plan = models.ForeignKey(
        "usuarios.PlanCurso",
        on_delete=models.PROTECT
    )

    dias_seleccionados = models.CharField(max_length=100)

    acepta_terminos = models.BooleanField(default=False)
    firma_digital = models.TextField(blank=True, null=True)

    codigo_barras = models.CharField(max_length=50, unique=True, blank=True)

    contacto_emergencia_nombre = models.CharField(max_length=150)
    contacto_emergencia_telefono = models.CharField(max_length=20)
    contacto_emergencia_trabajo = models.CharField(max_length=20, blank=True, null=True)
    contacto_emergencia_parentesco = models.CharField(max_length=50)

    def save(self, *args, **kwargs):

        if not self.folio:
            self.folio = f"CEF-{uuid.uuid4().hex[:8].upper()}"

        if not self.codigo_barras:
            self.codigo_barras = f"BAR-{uuid.uuid4().hex[:10].upper()}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.folio} - {self.nombre}"