from django.urls import path
from . import views

app_name = "pagos"

urlpatterns = [
    path("", views.escanear_pago, name="escanear_pago"),
    path("procesar/<int:preregistro_id>/", views.procesar_pago, name="procesar_pago"),

    # tarifas
    path("tarifas/", views.tarifa_lista, name="tarifa_lista"),
    path("tarifas/nuevo/", views.tarifa_crear, name="tarifa_crear"),
    path("tarifas/<int:pk>/editar/", views.tarifa_editar, name="tarifa_editar"),
    path("tarifas/<int:pk>/eliminar/", views.tarifa_eliminar, name="tarifa_eliminar"),
]