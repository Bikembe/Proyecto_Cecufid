from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('medico/', include('medico.urls')),
    path('', include('usuarios.urls')),
    path('accesos/', include('accesos.urls')),
    path('asignaciones/', include('asignaciones.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
