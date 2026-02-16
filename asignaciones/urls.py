from django.urls import path
from . import views

urlpatterns = [
    path('mis-horarios/', views.mis_horarios, name='mis_horarios'),
    path('horario/<int:horario_id>/', views.nadadores_horario, name='nadadores_horario'),
    path('evaluar/<int:inscripcion_id>/', views.evaluar_nadador, name='evaluar_nadador'),
    path('solicitudes/', views.solicitudes_pendientes, name='solicitudes_pendientes'),
    path('aprobar/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
]