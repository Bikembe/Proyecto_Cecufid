from django.db import models
from usuarios.models import Usuario, Nadador

class Alberca(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150)
    capacidad_maxima = models.IntegerField()
    estado = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


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


class Grupo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    alberca = models.ForeignKey(Alberca, on_delete=models.CASCADE)
    entrenador = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cupo_maximo = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Inscripcion(models.Model):
    nadador = models.ForeignKey(Nadador, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField()
    estado = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
