from django.contrib import admin
from .models import Acceso

@admin.register(Acceso)
class AccesoAdmin(admin.ModelAdmin):
    list_display = ("nadador", "tipo", "fecha")
    list_filter = ("tipo", "fecha")
    search_fields = ("nadador__nombre", "nadador__apellido_paterno", "nadador__codigo_barras")
    date_hierarchy = "fecha"
    ordering = ("-fecha",)