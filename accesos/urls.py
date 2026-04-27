from django.urls import path
from .views import escanear_acceso, historial_accesos, recuperaciones_hoy

app_name = "accesos"

urlpatterns = [
    path('escanear/', escanear_acceso, name='escanear'),
    path('historial/', historial_accesos, name='historial'),
    path('recuperaciones-hoy/', recuperaciones_hoy, name='recuperaciones_hoy'),
]