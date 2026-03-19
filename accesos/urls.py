from django.urls import path
from .views import escanear_acceso

urlpatterns = [
    path('escanear/', escanear_acceso, name='escanear'),
]