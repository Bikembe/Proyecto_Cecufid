from django.contrib import admin
from .models import Medico, CertificadoMedico


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cedula_profesional")
    search_fields = ("usuario__username", "cedula_profesional")


@admin.register(CertificadoMedico)
class CertificadoMedicoAdmin(admin.ModelAdmin):
    list_display = ("nadador", "medico", "fecha_examen")
    list_filter = ("fecha_examen",)
    search_fields = ("nadador__nombre",)
