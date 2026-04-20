from django.utils import timezone
from .models import HistorialAccion, UsuarioActivo

def registrar_accion(usuario, modulo, accion, descripcion="", request=None):

    ip = None
    user_agent = None

    if request:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    HistorialAccion.objects.create(
        usuario=usuario,
        modulo=modulo,
        accion=accion,
        descripcion=descripcion,
        ip_address=ip,
        user_agent=user_agent
    )

    if usuario:

        UsuarioActivo.objects.update_or_create(
            usuario=usuario,
            defaults={
                'ultima_actividad': timezone.now(),
                'conectado': True
            }
        )

def marcar_desconexion(usuario):
    UsuarioActivo.objects.filter(usuario=usuario).update(
        conectado=False
    )