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

    # =========================
    # CONTROL
    # =========================
    folio = models.CharField(max_length=20, unique=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE_EXAMEN'
    )

    # =========================
    # TIPO USUARIO
    # =========================
    es_menor = models.BooleanField(default=False)

    # =========================
    # DATOS PERSONALES
    # =========================
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

    # =========================
    # DOCUMENTOS ADULTO
    # =========================
    foto = models.ImageField(upload_to="preregistro/foto/")
    identificacion = models.ImageField(upload_to="preregistro/ine/", blank=True, null=True)

    # =========================
    # DOCUMENTOS MENOR
    # =========================
    acta_nacimiento = models.ImageField(upload_to="preregistro/acta/", blank=True, null=True)
    curp_documento = models.ImageField(upload_to="preregistro/curp/", blank=True, null=True)

    # Tutor
    nombre_tutor = models.CharField(max_length=200, blank=True, null=True)
    ine_tutor = models.ImageField(upload_to="preregistro/tutor/", blank=True, null=True)
    foto_tutor = models.ImageField(upload_to="preregistro/tutor_foto/", blank=True, null=True)

    # =========================
    # INSCRIPCIÓN
    # =========================
    categoria = models.ForeignKey(
        "usuarios.Categoria",
        on_delete=models.PROTECT
    )

    plan = models.ForeignKey(
        "usuarios.PlanCurso",
        on_delete=models.PROTECT
    )

    dias_seleccionados = models.CharField(max_length=100)

    # =========================
    # TERMINOS
    # =========================
    acepta_terminos = models.BooleanField(default=False)
    firma_digital = models.TextField(blank=True, null=True)

    # =========================
    # CODIGO DE BARRAS
    # =========================
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True)
    # 🔹 DATOS DE EMERGENCIA
    contacto_emergencia_nombre = models.CharField(max_length=150)
    contacto_emergencia_telefono = models.CharField(max_length=20)
    contacto_emergencia_trabajo = models.CharField(max_length=20, blank=True, null=True)
    contacto_emergencia_parentesco = models.CharField(max_length=50)
    # =========================
    # SAVE
    # =========================
    def save(self, *args, **kwargs):

        # Generar folio único
        if not self.folio:
            self.folio = f"CEF-{uuid.uuid4().hex[:8].upper()}"

        # Generar código de barras (usar folio)
        if not self.codigo_barras:
            self.codigo_barras = f"BAR-{uuid.uuid4().hex[:10].upper()}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.folio} - {self.nombre}"