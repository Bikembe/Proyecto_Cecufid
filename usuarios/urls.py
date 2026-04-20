from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    dashboard,
    usuario_lista,
    usuario_crear,
    usuario_editar,
    usuario_eliminar,
)

urlpatterns = [
    # 🔐 Autenticación
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),

    # 🏠 Dashboard
    path("", dashboard, name="dashboard"),

    # 👤 CRUD USUARIOS
    path("usuarios/", usuario_lista, name="usuarios_lista"),
    path("usuarios/nuevo/", usuario_crear, name="usuario_crear"),
    path("usuarios/editar/<int:pk>/", usuario_editar, name="usuario_editar"),
    path("usuarios/eliminar/<int:pk>/", usuario_eliminar, name="usuario_eliminar"),
]