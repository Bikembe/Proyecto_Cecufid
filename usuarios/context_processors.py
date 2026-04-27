from .menu import MENU_POR_ROL

def menu_usuario(request):
    if not request.user.is_authenticated:
        return {}

    rol = ""
    if request.user.rol:
        rol = request.user.rol.nombre

    menu = MENU_POR_ROL.get(rol, [])

    return {
        "menu_items": menu,
        "rol_usuario": rol
    }