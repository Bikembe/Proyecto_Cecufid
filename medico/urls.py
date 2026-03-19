from django.urls import path
from . import views

urlpatterns = [
    path("escanear/", views.escanear_medico, name="escanear_medico"),

    path("certificado/<int:nadador_id>/",
         views.crear_certificado,
         name="crear_certificado"),

    path("historial/<int:nadador_id>/",
         views.historial_medico,
         name="historial_medico"),

    path("imprimir/<int:certificado_id>/",
         views.imprimir_evaluacion,
         name="imprimir_evaluacion"),
]