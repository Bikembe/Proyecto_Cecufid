from django.contrib import admin
from .models import Alberca, Carril, Curso, Grupo, Asignacion, Inscripcion


@admin.register(Alberca)
class AlbercaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'capacidad_maxima', 'estado']
    search_fields = ['nombre']


@admin.register(Carril)
class CarrilAdmin(admin.ModelAdmin):
    list_display = ['numero', 'alberca', 'profundidad', 'capacidad_usuarios', 'estado']
    list_filter = ['alberca', 'estado']


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nivel', 'duracion_semanas', 'costo']
    list_filter = ['nivel']


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ['curso', 'entrenador', 'alberca', 'carril', 'turno', 'cupo_maximo', 'activo']
    list_filter = ['turno', 'activo', 'alberca']


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ['carril', 'entrenador', 'grupo', 'dia_semana', 'hora_inicio', 'hora_fin', 'activa']
    list_filter = ['dia_semana', 'activa']


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ['nadador', 'grupo', 'fecha_inscripcion', 'estado']
    list_filter = ['estado']