from django.db import models


class Alberca(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150)
    capacidad_maxima = models.IntegerField()
    estado = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'asignaciones_alberca'
        managed = False


class Nivel(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'asignaciones_nivel'
        managed = False


class Carril(models.Model):
    numero = models.IntegerField()
    estado = models.CharField(max_length=20, default='disponible')
    profundidad = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    capacidad_usuarios = models.IntegerField(default=10)
    alberca = models.ForeignKey(Alberca, on_delete=models.CASCADE, related_name='carriles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Carril {self.numero}'

    class Meta:
        db_table = 'asignaciones_carril'
        managed = False
        ordering = ['numero']


class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=50)
    descripcion = models.TextField()
    duracion_semanas = models.IntegerField()
    costo = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'asignaciones_curso'
        managed = False


# Modelo para usuarios_usuario (BD real usa AbstractUser de Django)
class Usuario(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    estado = models.BooleanField(default=True)
    apellido_materno = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def nombre(self):
        return self.first_name

    @property
    def apellido_paterno(self):
        return self.last_name

    class Meta:
        db_table = 'usuarios_usuario'
        managed = False


class Nadador(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    codigo_barras = models.CharField(max_length=100, blank=True)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    estado = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido_paterno}'

    class Meta:
        db_table = 'usuarios_nadador'
        managed = False


class HorarioCarril(models.Model):
    """Tabla real en BD: asignaciones_horariocarril"""
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    capacidad_maxima = models.IntegerField()
    carril = models.ForeignKey(Carril, on_delete=models.CASCADE, related_name='horarios')
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='horarios')
    maestro = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='horarios')

    def __str__(self):
        return f'Carril {self.carril.numero} | {self.hora_inicio}-{self.hora_fin}'

    def hay_choque_maestro(self):
        return HorarioCarril.objects.filter(
            maestro=self.maestro,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
        ).exclude(pk=self.pk).exists()

    def hay_choque_carril(self):
        return HorarioCarril.objects.filter(
            carril=self.carril,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
        ).exclude(pk=self.pk).exists()

    class Meta:
        db_table = 'asignaciones_horariocarril'
        managed = False


class Grupo(models.Model):
    TURNO_CHOICES = [
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino'),
        ('nocturno', 'Nocturno'),
    ]

    cupo_maximo = models.IntegerField()
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, default='matutino')
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    alberca = models.ForeignKey(Alberca, on_delete=models.CASCADE, related_name='grupos')
    carril = models.ForeignKey(Carril, on_delete=models.SET_NULL, null=True, blank=True, related_name='grupos')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='grupos')
    entrenador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='grupos')

    def __str__(self):
        return f'{self.curso.nombre} - {self.entrenador}'

    def inscritos_count(self):
        return self.inscripciones.filter(estado='activo').count()

    def hay_cupo(self):
        return self.inscritos_count() < self.cupo_maximo

    class Meta:
        db_table = 'asignaciones_grupo'
        managed = False


class Inscripcion(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]

    fecha_inscripcion = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name='inscripciones')
    nadador = models.ForeignKey(Nadador, on_delete=models.CASCADE, related_name='inscripciones')

    def __str__(self):
        return f'{self.nadador} → {self.grupo}'

    class Meta:
        db_table = 'asignaciones_inscripcion'
        managed = False


# Mantenemos Asignacion para el historial y cuadrícula
class Asignacion(models.Model):
    DIA_CHOICES = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]

    carril = models.ForeignKey(Carril, on_delete=models.CASCADE, related_name='asignaciones')
    entrenador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='asignaciones')
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name='asignaciones')
    dia_semana = models.CharField(max_length=15, choices=DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.carril} | {self.dia_semana} {self.hora_inicio}-{self.hora_fin}'

    def hay_choque_maestro(self):
        return Asignacion.objects.filter(
            entrenador=self.entrenador,
            dia_semana=self.dia_semana,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
            activa=True,
        ).exclude(pk=self.pk).exists()

    def hay_choque_carril(self):
        return Asignacion.objects.filter(
            carril=self.carril,
            dia_semana=self.dia_semana,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
            activa=True,
        ).exclude(pk=self.pk).exists()

    class Meta:
        db_table = 'asignaciones_asignacion'
        ordering = ['dia_semana', 'hora_inicio']