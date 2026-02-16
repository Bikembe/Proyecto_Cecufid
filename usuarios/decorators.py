from django.core.exceptions import PermissionDenied


def rol_requerido(roles_permitidos=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.rol.nombre in roles_permitidos:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator