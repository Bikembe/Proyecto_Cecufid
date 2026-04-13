from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from usuarios.decorators import rol_requerido
from asignaciones.models import InscripcionCarril, HorarioCarril
from .models import Evaluacion


@login_required
@rol_requerido(['Maestro'])
def evaluaciones(request):

    horarios = HorarioCarril.objects.filter(maestro=request.user)

    inscripciones = InscripcionCarril.objects.filter(
        horario_carril__maestro=request.user,
        activo=True
    ).select_related("nadador", "horario_carril")

    return render(request, "evaluaciones/formulario.html", {
        "horarios": horarios,
        "inscripciones": inscripciones
    })


@login_required
@rol_requerido(['Maestro'])
def evaluar_nadador(request, inscripcion_id):

    inscripcion = get_object_or_404(InscripcionCarril, id=inscripcion_id)

    if request.method == "POST":

        Evaluacion.objects.create(
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

        return redirect("evaluaciones:historial")

    return render(request, "evaluaciones/formulario.html", {
        "inscripcion": inscripcion
    })


@login_required
@rol_requerido(['Maestro'])
def detalle_evaluacion(request, id):

    evaluacion = get_object_or_404(Evaluacion, id=id)

    return render(request, "evaluaciones/detalle.html", {
        "evaluacion": evaluacion
    })


@login_required
@rol_requerido(['Maestro'])
def historial_maestro(request):

    evaluaciones = Evaluacion.objects.filter(
        maestro=request.user
    ).order_by("-fecha")

    return render(request, "evaluaciones/historial.html", {
        "evaluaciones": evaluaciones
    })


@login_required
@rol_requerido(['Administrador'])
def revisar_evaluaciones(request):

    evaluaciones = Evaluacion.objects.select_related(
        "nadador", "maestro", "horario_carril"
    ).order_by("-fecha")

    return render(request, "evaluaciones/revision.html", {
        "evaluaciones": evaluaciones
    })


@login_required
@rol_requerido(['Maestro', 'Administrador'])
def solicitar_promocion(request, evaluacion_id):

    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)

    if evaluacion.promedio >= 4.0:
        evaluacion.estado_promocion = "APROBADA"
        evaluacion.save()

    elif evaluacion.promedio >= 3.0:
        evaluacion.estado_promocion = "EN_REVISION"
        evaluacion.save()

    else:
        evaluacion.estado_promocion = "RECHAZADA"
        evaluacion.save()

    return redirect("evaluaciones:historial")

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

    return render(request, "evaluaciones/dashboard.html", {
        "evaluaciones": evaluaciones[:10],
        "total": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "promedio_general": promedio_general
    })

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

    return render(request, "evaluaciones/app_dashboard.html", {
        "evaluaciones": evaluaciones[:15],
        "total": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "promedio_general": promedio_general
    })

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

    return render(request, "evaluaciones/panel_maestro.html", {
        "horarios": horarios,
        "inscripciones": inscripciones,
        "evaluaciones": evaluaciones
    })

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

    return render(request, "evaluaciones/panel_admin.html", {
        "evaluaciones": evaluaciones[:20],
        "total": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "promedio_general": promedio_general
    })

