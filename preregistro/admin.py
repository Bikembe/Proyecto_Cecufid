from django.contrib import admin
from .models import PreRegistro


@admin.register(PreRegistro)
class PreRegistroAdmin(admin.ModelAdmin):
    list_display = (
        "folio", "nombre", "apellido_paterno",
        "telefono", "estado"
    )
    list_filter = ("estado", "sexo")
    search_fields = (
        "folio",
        "nombre",
        "apellido_paterno",
        "telefono",
        "correo",
    )
    readonly_fields = ("folio",)