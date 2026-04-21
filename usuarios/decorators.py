from django.core.exceptions import PermissionDenied
from functools import wraps

def rol_requerido(roles_permitidos=None):
    if roles_permitidos is None:
        roles_permitidos = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            try:
                rol_usuario = request.user.rol.nombre
            except:
                raise PermissionDenied

            if rol_usuario not in roles_permitidos:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator