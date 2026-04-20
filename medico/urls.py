from django.urls import path
from . import views

app_name = "medico"

urlpatterns = [
    path("escanear/", views.escanear_medico, name="escanear"),

    path("crear/<int:nadador_id>/", views.crear_certificado, name="crear_certificado"),
    path("crear-preregistro/<int:preregistro_id>/", views.crear_certificado_preregistro, name="crear_certificado_preregistro"),

    path("historial/<int:nadador_id>/", views.historial_medico, name="historial_medico"),
    path("historial-preregistro/<int:preregistro_id>/", views.historial_medico_preregistro, name="historial_medico_preregistro"),
    path("historial-general/", views.historial_general, name="historial_general"),

    path("imprimir/<int:certificado_id>/", views.imprimir_evaluacion, name="imprimir_evaluacion"),
    
    path("medicos/", views.medico_lista, name="medico_lista"),
    path("medicos/nuevo/", views.medico_crear, name="medico_crear"),
    path("medicos/<int:pk>/editar/", views.medico_editar, name="medico_editar"),
    path("medicos/<int:pk>/eliminar/", views.medico_eliminar, name="medico_eliminar"),
]