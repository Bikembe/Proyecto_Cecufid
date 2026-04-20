from django.utils import timezone
from .models import UsuarioActivo, HistorialAccion


class HistorialMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        user = getattr(request, "user", None)

        if user and user.is_authenticated:

            UsuarioActivo.objects.update_or_create(
                usuario=user,
                defaults={
                    "ultima_actividad": timezone.now(),
                    "conectado": True
                }
            )

            HistorialAccion.objects.create(
                usuario=user,
                modulo="SISTEMA",
                accion="CONSULTA",
                descripcion=request.path,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")
            )

        return response

    def get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0]
        return request.META.get("REMOTE_ADDR")