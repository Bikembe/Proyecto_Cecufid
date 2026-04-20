from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario, Rol, Sede, PlanCurso, Categoria
from reportes.utils import registrar_accion


# =========================
# LOGIN
# =========================
class CustomLoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)

        registrar_accion(
            usuario=self.request.user,
            modulo="SISTEMA",
            accion="LOGIN",
            descripcion="Inicio de sesión",
            request=self.request
        )

        return response


# =========================
# LOGOUT
# =========================
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            registrar_accion(
                usuario=request.user,
                modulo="SISTEMA",
                accion="LOGOUT",
                descripcion="Cierre de sesión",
                request=request
            )
        return super().dispatch(request, *args, **kwargs)


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):

    registrar_accion(
        usuario=request.user,
        modulo="SISTEMA",
        accion="CONSULTA",
        descripcion="Acceso al dashboard",
        request=request
    )

    if not request.user.rol:
        return render(request, "dashboard.html")

    rol = request.user.rol.nombre

    if rol == "Administrador":
        return render(request, "dashboard.html")

    elif rol == "Maestro":
        return redirect("evaluaciones:app_dashboard")

    elif rol == "Medico":
        return redirect("medico:escanear_medico")

    elif rol == "Caja":
        return render(request, "dashboard.html")

    elif rol == "Recepcion":
        return redirect("accesos:escanear")

    return render(request, "dashboard.html")


# =========================
# USUARIOS DEL SISTEMA
# =========================

@login_required
def usuario_lista(request):

    registrar_accion(
        usuario=request.user,
        modulo="USUARIOS",
        accion="CONSULTA",
        descripcion="Listado de usuarios",
        request=request
    )

    usuarios = Usuario.objects.select_related("rol").all()

    return render(request, "usuarios/usuarios_lista.html", {
        "usuarios": usuarios
    })


@login_required
def usuario_crear(request):
    roles = Rol.objects.all()

    if request.method == "POST":

        usuario = Usuario.objects.create(
            email=request.POST.get("email"),
            first_name=request.POST.get("nombre"),
            last_name=request.POST.get("apellido_paterno"),
            apellido_materno=request.POST.get("apellido_materno"),
            rol_id=request.POST.get("rol"),
            estado=request.POST.get("estado")
        )
        usuario.set_password(request.POST.get("password"))
        usuario.save()

        registrar_accion(
            usuario=request.user,
            modulo="USUARIOS",
            accion="CREAR",
            descripcion=f"Creó usuario {usuario.email}",
            request=request
        )

        return redirect("usuarios_lista")

    return render(request, "usuarios/usuario_form.html", {
        "roles": roles
    })


@login_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    roles = Rol.objects.all()

    if request.method == "POST":

        usuario.email = request.POST.get("email")
        usuario.first_name = request.POST.get("nombre")
        usuario.last_name = request.POST.get("apellido_paterno")
        usuario.apellido_materno = request.POST.get("apellido_materno")
        usuario.rol_id = request.POST.get("rol")
        usuario.estado = request.POST.get("estado")

        if request.POST.get("password"):
            usuario.set_password(request.POST.get("password"))

        usuario.save()

        registrar_accion(
            usuario=request.user,
            modulo="USUARIOS",
            accion="EDITAR",
            descripcion=f"Editó usuario {usuario.email}",
            request=request
        )

        return redirect("usuarios_lista")

    return render(request, "usuarios/usuario_form.html", {
        "usuario": usuario,
        "roles": roles
    })


@login_required
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    registrar_accion(
        usuario=request.user,
        modulo="USUARIOS",
        accion="ELIMINAR",
        descripcion=f"Eliminó usuario {usuario.email}",
        request=request
    )

    usuario.delete()

    return redirect("usuarios_lista")


# =========================
# PLAN CURSOS
# =========================

@login_required
def plan_lista(request):

    registrar_accion(
        usuario=request.user,
        modulo="PLANES",
        accion="CONSULTA",
        descripcion="Listado de planes de curso",
        request=request
    )

    planes = PlanCurso.objects.select_related("sede", "categoria").all()

    return render(request, "usuarios/plan_lista.html", {
        "planes": planes
    })


@login_required
def plan_crear(request):
    sedes = Sede.objects.all()
    categorias = Categoria.objects.all()

    if request.method == "POST":

        plan = PlanCurso.objects.create(
            nombre=request.POST.get("nombre"),
            tipo_curso=request.POST.get("tipo_curso"),
            sede_id=request.POST.get("sede"),
            categoria_id=request.POST.get("categoria"),
            dias_permitidos=request.POST.get("dias"),
            horario_inicio=request.POST.get("hora_inicio"),
            horario_fin=request.POST.get("hora_fin"),
            duracion_dias=request.POST.get("duracion"),
            precio=request.POST.get("precio"),
            activo=True if request.POST.get("activo") else False
        )

        registrar_accion(
            usuario=request.user,
            modulo="PLANES",
            accion="CREAR",
            descripcion=f"Creó plan {plan.nombre}",
            request=request
        )

        return redirect("plan_lista")

    return render(request, "usuarios/plan_form.html", {
        "sedes": sedes,
        "categorias": categorias
    })


@login_required
def plan_editar(request, pk):
    plan = get_object_or_404(PlanCurso, pk=pk)
    sedes = Sede.objects.all()
    categorias = Categoria.objects.all()

    if request.method == "POST":

        plan.nombre = request.POST.get("nombre")
        plan.tipo_curso = request.POST.get("tipo_curso")
        plan.sede_id = request.POST.get("sede")
        plan.categoria_id = request.POST.get("categoria")
        plan.dias_permitidos = request.POST.get("dias")
        plan.horario_inicio = request.POST.get("hora_inicio")
        plan.horario_fin = request.POST.get("hora_fin")
        plan.duracion_dias = request.POST.get("duracion")
        plan.precio = request.POST.get("precio")
        plan.activo = True if request.POST.get("activo") else False

        plan.save()

        registrar_accion(
            usuario=request.user,
            modulo="PLANES",
            accion="EDITAR",
            descripcion=f"Editó plan {plan.nombre}",
            request=request
        )

        return redirect("plan_lista")

    return render(request, "usuarios/plan_form.html", {
        "plan": plan,
        "sedes": sedes,
        "categorias": categorias
    })


@login_required
def plan_eliminar(request, pk):
    plan = get_object_or_404(PlanCurso, pk=pk)

    registrar_accion(
        usuario=request.user,
        modulo="PLANES",
        accion="ELIMINAR",
        descripcion=f"Eliminó plan {plan.nombre}",
        request=request
    )

    plan.delete()

    return redirect("plan_lista")