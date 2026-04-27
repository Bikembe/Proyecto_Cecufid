from django.contrib import admin
from .models import EventoCalendario, RecuperacionClase, CupoRecuperacion


@admin.register(EventoCalendario)
class EventoCalendarioAdmin(admin.ModelAdmin):
    list_display = ("tipo", "fecha", "horario_carril", "permite_recuperacion", "creado_por")
    list_filter = ("tipo", "permite_recuperacion", "fecha")
    search_fields = ("motivo",)
    date_hierarchy = "fecha"


@admin.register(RecuperacionClase)
class RecuperacionClaseAdmin(admin.ModelAdmin):
    list_display = ("inscripcion", "horario_carril", "fecha", "nivel", "estado")
    list_filter = ("fecha", "nivel", "estado")
    search_fields = (
        "inscripcion__nadador__nombre",
    )
    date_hierarchy = "fecha"


@admin.register(CupoRecuperacion)
class CupoRecuperacionAdmin(admin.ModelAdmin):
    list_display = ("horario_carril", "nivel", "maximo_nadadores", "activo")
    list_filter = ("nivel", "activo")