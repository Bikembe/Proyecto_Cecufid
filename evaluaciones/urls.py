from django.urls import path
from . import views

app_name = "evaluaciones"

urlpatterns = [

    path('maestro/', views.panel_maestro, name='panel_maestro'),
    path('maestro/evaluar/<int:inscripcion_id>/', views.evaluar_nadador, name='evaluar'),
    path('maestro/historial/', views.historial_maestro, name='historial'),
    path("app/", views.app_dashboard, name="app_dashboard"),
    path('detalle/<int:id>/', views.detalle_evaluacion, name='detalle'),
    path('admin/', views.panel_admin, name='panel_admin'),
    path('admin/evaluaciones/', views.revisar_evaluaciones, name='revision'),
]