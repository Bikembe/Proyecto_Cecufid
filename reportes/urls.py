from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    path('historial/', views.historial_lista, name='historial_lista'),
    path('online/', views.usuarios_en_linea, name='usuarios_en_linea'),
    path('lista/', views.reporte_lista, name='reporte_lista'),
    path('caja/', views.reporte_caja, name='reporte_caja'),
    path('excel/', views.exportar_excel_caja, name='excel_caja'),
    path('grafica/', views.grafica_ingresos, name='grafica_ingresos'),
    path('corte/', views.corte_caja, name='corte_caja'),
    path('mensual/', views.reporte_mensual, name='reporte_mensual'),
    path('sede/', views.reporte_por_sede, name='reporte_sede'),
]