from django.urls import path
from . import views

app_name = "pagos"

urlpatterns = [
    path("", views.escanear_pago, name="escanear_pago"),
    path("procesar/<int:preregistro_id>/", views.procesar_pago, name="procesar_pago"),

    path("tarifas/", views.tarifa_lista, name="tarifa_lista"),
    path("tarifas/nuevo/", views.tarifa_crear, name="tarifa_crear"),
    path("tarifas/<int:pk>/editar/", views.tarifa_editar, name="tarifa_editar"),
    path("tarifas/<int:pk>/eliminar/", views.tarifa_eliminar, name="tarifa_eliminar"),

    path("productos/", views.producto_lista, name="producto_lista"),
    path("productos/crear/", views.producto_crear, name="producto_crear"),
    path("productos/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path("productos/<int:pk>/eliminar/", views.producto_eliminar, name="producto_eliminar"),

    path("historial/<int:nadador_id>/", views.historial_nadador, name="historial_nadador"),
]