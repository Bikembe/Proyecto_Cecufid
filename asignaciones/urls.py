from django.urls import path
from . import views

app_name = 'asignaciones'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('carriles/', views.carril_lista, name='carril_lista'),
    path('carriles/nuevo/', views.carril_crear, name='carril_crear'),
    path('carriles/<int:pk>/editar/', views.carril_editar, name='carril_editar'),
    path('carriles/<int:pk>/eliminar/', views.carril_eliminar, name='carril_eliminar'),

    path('horarios/', views.horario_lista, name='horario_lista'),
    path('horarios/nuevo/', views.horario_crear, name='horario_crear'),
    path('horarios/<int:pk>/editar/', views.horario_editar, name='horario_editar'),
    path('horarios/<int:pk>/eliminar/', views.horario_eliminar, name='horario_eliminar'),

    path('cuadricula/', views.asignacion_cuadricula, name='cuadricula'),

    path('reportes/', views.reporte_uso_carriles, name='reporte'),
    path('grupo/<int:pk>/', views.grupo_detalle, name='grupo_detalle'),

    path('inscripciones/', views.inscripcion_lista, name='inscripcion_lista'),
    path('inscripciones/nuevo/', views.inscripcion_crear, name='inscripcion_crear'),
    path('inscripciones/<int:pk>/baja/', views.inscripcion_baja, name='inscripcion_baja'),

    path('api/horarios/', views.api_horarios, name='api_horarios'),
    path('niveles/nuevo/', views.nivel_crear, name='nivel_crear'),
]