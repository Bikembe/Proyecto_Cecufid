from django.urls import path
from .views import escanear_acceso, historial_accesos

app_name = "accesos"

urlpatterns = [
    path('escanear/', escanear_acceso, name='escanear'),
    path('historial/', historial_accesos, name='historial'),
]