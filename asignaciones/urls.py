from django.urls import path
from . import views

app_name = 'asignaciones'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Carriles
    path('carriles/', views.carril_lista, name='carril_lista'),
    path('carriles/nuevo/', views.carril_crear, name='carril_crear'),
    path('carriles/<int:pk>/editar/', views.carril_editar, name='carril_editar'),
    path('carriles/<int:pk>/eliminar/', views.carril_eliminar, name='carril_eliminar'),

    # Horarios de carril (asignación real maestro+carril+nivel)
    path('horarios/', views.horario_lista, name='horario_lista'),
    path('horarios/nuevo/', views.horario_crear, name='horario_crear'),
    path('horarios/<int:pk>/editar/', views.horario_editar, name='horario_editar'),
    path('horarios/<int:pk>/eliminar/', views.horario_eliminar, name='horario_eliminar'),

    # Cuadrícula visual
    path('cuadricula/', views.asignacion_cuadricula, name='cuadricula'),

    # Grupos
    path('grupos/', views.grupo_lista, name='grupo_lista'),
    path('grupos/nuevo/', views.grupo_crear, name='grupo_crear'),
    path('grupos/<int:pk>/', views.grupo_detalle, name='grupo_detalle'),
    path('grupos/<int:pk>/editar/', views.grupo_editar, name='grupo_editar'),
    path('grupos/<int:pk>/eliminar/', views.grupo_eliminar, name='grupo_eliminar'),
    path('grupos/<int:grupo_pk>/inscribir/', views.inscripcion_crear, name='inscripcion_crear'),

    # Inscripciones
    path('inscripciones/<int:pk>/baja/', views.inscripcion_baja, name='inscripcion_baja'),

    # Reportes
    path('reportes/', views.reporte_uso_carriles, name='reporte'),

    # API
    path('api/carriles/<int:alberca_id>/', views.api_carriles_por_alberca, name='api_carriles'),
]