from django.urls import path
from . import views

app_name = "calendario"

urlpatterns = [

    path('', views.calendario_lista, name='calendario_lista'),

    path('recepcion/recuperacion/', views.recepcion_recuperacion, name='recepcion_recuperacion'),

    path('cancelar-dia/', views.cancelar_dia, name='cancelar_dia'),
    path('cancelar-horario/', views.cancelar_horario, name='cancelar_horario'),

    path('ocupacion/', views.ocupacion_recuperaciones, name='ocupacion_recuperaciones'),

    path('api/horarios-disponibles/', views.horarios_disponibles, name='api_horarios'),
    path('api/cupo/', views.api_cupo, name='api_cupo'),

    path('api/detalle-horario/', views.detalle_horario, name='detalle_horario'),

    path('api/agendar/', views.agendar_desde_calendario, name='agendar_calendario'),
]