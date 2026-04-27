from django.contrib import admin
from .models import CertificadoMedico, Medico


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "usuario", "cedula_profesional")
    search_fields = ("nombre_completo", "cedula_profesional")


@admin.register(CertificadoMedico)
class CertificadoMedicoAdmin(admin.ModelAdmin):
    list_display = ("nadador", "preregistro", "medico", "estatus", "fecha_examen")
    list_filter = ("estatus", "fecha_examen", "medico")
    search_fields = (
        "nadador__nombre",
        "preregistro__nombre",
        "medico__nombre_completo",
    )
    date_hierarchy = "fecha_examen"