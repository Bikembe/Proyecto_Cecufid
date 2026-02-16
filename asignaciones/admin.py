from django.contrib import admin
from .models import (
    Nivel,
    Carril,
    HorarioCarril,
    InscripcionCarril,
    Evaluacion,
    SolicitudPromocion,
)


@admin.register(HorarioCarril)
class HorarioCarrilAdmin(admin.ModelAdmin):
    list_display = ('carril', 'nivel', 'maestro', 'hora_inicio', 'hora_fin', 'capacidad_maxima', 'cupo_ocupado')
    list_filter = ('nivel', 'maestro')
    search_fields = ('carril__numero',)


@admin.register(InscripcionCarril)
class InscripcionCarrilAdmin(admin.ModelAdmin):
    list_display = ('nadador', 'horario_carril', 'activo')
    list_filter = ('activo', 'horario_carril__maestro')


admin.site.register(Nivel)
admin.site.register(Carril)
admin.site.register(Evaluacion)
admin.site.register(SolicitudPromocion)