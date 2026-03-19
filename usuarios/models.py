from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):

    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )

    username = None
    email = models.EmailField(unique=True)

    apellido_materno = models.CharField(max_length=100)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='activo'
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Nadador(models.Model):

    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )

    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )

    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)

    codigo_barras = models.CharField(max_length=50, unique=True)

    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)

    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True, null=True)

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='activo'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"

class Sede(models.Model):
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    edad_min = models.PositiveIntegerField()
    edad_max = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre


class PlanCurso(models.Model):

    TIPO_CURSO = (
        ('ANUAL', 'Curso Anual'),
        ('VERANO', 'Curso de Verano'),
        ('INTENSIVO', 'Curso Intensivo'),
    )

    DIAS_SEMANA = (
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    )

    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=150)
    tipo_curso = models.CharField(max_length=20, choices=TIPO_CURSO)

    dias_permitidos = models.CharField(max_length=50)
    horario_inicio = models.TimeField()
    horario_fin = models.TimeField()

    duracion_dias = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.sede}"


class Inscripcion(models.Model):

    nadador = models.ForeignKey(Nadador, on_delete=models.CASCADE)
    plan = models.ForeignKey(PlanCurso, on_delete=models.PROTECT)

    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(blank=True)

    def save(self, *args, **kwargs):
        if not self.fecha_fin:
            self.fecha_fin = self.fecha_inicio + timedelta(days=self.plan.duracion_dias)
        super().save(*args, **kwargs)

    def esta_vigente(self):
        return self.fecha_fin >= timezone.now().date()

    def __str__(self):
        return f"{self.nadador} - {self.plan}"