from django.urls import path
from . import views

app_name = "preregistro"

urlpatterns = [
    path("nuevo/", views.crear_preregistro, name="crear"),
     path("detalle/<int:pk>/", views.detalle_preregistro, name="detalle"),
]