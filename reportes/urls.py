from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    path('historial/', views.historial_lista, name='historial_lista'),
    path('online/', views.usuarios_en_linea, name='usuarios_en_linea'),
    path('lista/', views.reporte_lista, name='reporte_lista'),
]