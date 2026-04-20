from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from usuarios.decorators import rol_requerido
from asignaciones.models import InscripcionCarril, HorarioCarril
from .models import Evaluacion
from reportes.utils import registrar_accion


# =========================
# FORMULARIO PRINCIPAL
# =========================
@login_required
@rol_requerido(['Maestro'])
def evaluaciones(request):

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="CONSULTA",
        descripcion="Accedió al módulo de evaluaciones (formulario maestro)",
        request=request
    )

    horarios = HorarioCarril.objects.filter(maestro=request.user)

    inscripciones = InscripcionCarril.objects.filter(
        horario_carril__maestro=request.user,
        activo=True
    ).select_related("nadador", "horario_carril")

    return render(request, "evaluaciones/formulario.html", {
        "horarios": horarios,
        "inscripciones": inscripciones
    })


# =========================
# CALIFICAR NADADOR
# =========================
@login_required
@rol_requerido(['Maestro'])
def evaluar_nadador(request, inscripcion_id):

    inscripcion = get_object_or_404(InscripcionCarril, id=inscripcion_id)

    if request.method == "POST":

        evaluacion = Evaluacion.objects.create(
            nadador=inscripcion.nadador,
            horario_carril=inscripcion.horario_carril,
            maestro=request.user,

            respiracion=int(request.POST.get("respiracion", 0)),
            libre=int(request.POST.get("libre", 0)),
            espalda=int(request.POST.get("espalda", 0)),
            mariposa=int(request.POST.get("mariposa", 0)),
            resistencia=int(request.POST.get("resistencia", 0)),

            observaciones=request.POST.get("observaciones")
        )

        registrar_accion(
            usuario=request.user,
            modulo="EVALUACIONES",
            accion="CREAR",
            descripcion=f"Evaluó nadador {inscripcion.nadador}",
            request=request
        )

        return redirect("evaluaciones:historial")

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="CONSULTA",
        descripcion=f"Abrió formulario de evaluación para {inscripcion.nadador}",
        request=request
    )

    return render(request, "evaluaciones/formulario.html", {
        "inscripcion": inscripcion
    })


# =========================
# DETALLE EVALUACIÓN
# =========================
@login_required
@rol_requerido(['Maestro'])
def detalle_evaluacion(request, id):

    evaluacion = get_object_or_404(Evaluacion, id=id)

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="CONSULTA",
        descripcion=f"Vio detalle de evaluación ID {evaluacion.id}",
        request=request
    )

    return render(request, "evaluaciones/detalle.html", {
        "evaluacion": evaluacion
    })


# =========================
# HISTORIAL MAESTRO
# =========================
@login_required
@rol_requerido(['Maestro'])
def historial_maestro(request):

    evaluaciones = Evaluacion.objects.filter(
        maestro=request.user
    ).order_by("-fecha")

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="CONSULTA",
        descripcion="Consultó historial de evaluaciones",
        request=request
    )

    return render(request, "evaluaciones/historial.html", {
        "evaluaciones": evaluaciones
    })


# =========================
# REVISIÓN ADMIN
# =========================
@login_required
@rol_requerido(['Administrador'])
def revisar_evaluaciones(request):

    evaluaciones = Evaluacion.objects.select_related(
        "nadador", "maestro", "horario_carril"
    ).order_by("-fecha")

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="CONSULTA",
        descripcion="Revisó todas las evaluaciones (admin)",
        request=request
    )

    return render(request, "evaluaciones/revision.html", {
        "evaluaciones": evaluaciones
    })


# =========================
# PROMOCIÓN
# =========================
@login_required
@rol_requerido(['Maestro', 'Administrador'])
def solicitar_promocion(request, evaluacion_id):

    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)

    if evaluacion.promedio >= 4.0:
        evaluacion.estado_promocion = "APROBADA"
    elif evaluacion.promedio >= 3.0:
        evaluacion.estado_promocion = "EN_REVISION"
    else:
        evaluacion.estado_promocion = "RECHAZADA"

    evaluacion.save()

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="EDITAR",
        descripcion=f"Solicitó promoción para evaluación {evaluacion.id} ({evaluacion.estado_promocion})",
        request=request
    )

    return redirect("evaluaciones:historial")


# =========================
# DASHBOARD MAESTRO
# =========================
@login_required
@rol_requerido(['Maestro', 'Administrador'])
def dashboard_evaluaciones(request):

    evaluaciones = Evaluacion.objects.select_related(
        "nadador", "horario_carril"
    ).order_by("-fecha")

    total = evaluaciones.count()
    aprobados = evaluaciones.filter(promedio__gte=4).count()
    reprobados = evaluaciones.filter(promedio__lt=3).count()

    promedio_general = 0
    if total > 0:
        promedio_general = sum([e.promedio for e in evaluaciones]) / total

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="CONSULTA",
        descripcion="Accedió al dashboard de evaluaciones",
        request=request
    )

    return render(request, "evaluaciones/dashboard.html", {
        "evaluaciones": evaluaciones[:10],
        "total": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "promedio_general": promedio_general
    })


# =========================
# APP DASHBOARD
# =========================
@login_required
def app_dashboard(request):

    evaluaciones = Evaluacion.objects.select_related(
        "nadador", "horario_carril"
    ).order_by("-fecha")

    total = evaluaciones.count()
    aprobados = evaluaciones.filter(promedio__gte=4).count()
    reprobados = evaluaciones.filter(promedio__lt=3).count()

    promedio_general = 0
    if total > 0:
        promedio_general = sum([e.promedio for e in evaluaciones]) / total

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="CONSULTA",
        descripcion="Accedió al dashboard general de app evaluaciones",
        request=request
    )

    return render(request, "evaluaciones/app_dashboard.html", {
        "evaluaciones": evaluaciones[:15],
        "total": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "promedio_general": promedio_general
    })


# =========================
# PANEL MAESTRO
# =========================
@login_required
@rol_requerido(['Maestro'])
def panel_maestro(request):

    horarios = HorarioCarril.objects.filter(maestro=request.user)

    inscripciones = InscripcionCarril.objects.filter(
        horario_carril__maestro=request.user,
        activo=True
    ).select_related("nadador", "horario_carril")

    evaluaciones = Evaluacion.objects.filter(
        maestro=request.user
    ).order_by("-fecha")

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="CONSULTA",
        descripcion="Accedió al panel del maestro",
        request=request
    )

    return render(request, "evaluaciones/panel_maestro.html", {
        "horarios": horarios,
        "inscripciones": inscripciones,
        "evaluaciones": evaluaciones
    })


# =========================
# PANEL ADMIN
# =========================
@login_required
@rol_requerido(['Administrador'])
def panel_admin(request):

    evaluaciones = Evaluacion.objects.select_related(
        "nadador", "maestro", "horario_carril"
    ).order_by("-fecha")

    total = evaluaciones.count()
    aprobados = evaluaciones.filter(promedio__gte=4).count()
    reprobados = evaluaciones.filter(promedio__lt=3).count()

    promedio_general = 0
    if total > 0:
        promedio_general = sum([e.promedio for e in evaluaciones]) / total

    registrar_accion(
        usuario=request.user,
        modulo="EVALUACIONES",
        accion="CONSULTA",
        descripcion="Accedió al panel administrativo de evaluaciones",
        request=request
    )

    return render(request, "evaluaciones/panel_admin.html", {
        "evaluaciones": evaluaciones[:20],
        "total": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "promedio_general": promedio_general
    })