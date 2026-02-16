from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import (
    HorarioCarril,
    InscripcionCarril,
    Evaluacion,
    SolicitudPromocion,
    Nivel
)


@login_required
def mis_horarios(request):
    horarios = HorarioCarril.objects.filter(maestro=request.user)
    return render(request, 'asignaciones/mis_horarios.html', {
        'horarios': horarios
    })


@login_required
def nadadores_horario(request, horario_id):
    horario = get_object_or_404(HorarioCarril, id=horario_id, maestro=request.user)

    inscripciones = InscripcionCarril.objects.filter(
        horario_carril=horario,
        activo=True
    ).select_related('nadador')

    return render(request, 'asignaciones/nadadores_horario.html', {
        'horario': horario,
        'inscripciones': inscripciones
    })


@login_required
def evaluar_nadador(request, inscripcion_id):
    inscripcion = get_object_or_404(
        InscripcionCarril,
        id=inscripcion_id,
        horario_carril__maestro=request.user
    )

    horario = inscripcion.horario_carril
    nadador = inscripcion.nadador

    if request.method == 'POST':
        aprobado = request.POST.get('aprobado') == 'on'
        observaciones = request.POST.get('observaciones')
        nivel_sugerido_id = request.POST.get('nivel_sugerido')

        evaluacion = Evaluacion.objects.create(
            nadador=nadador,
            horario_carril=horario,
            aprobado=aprobado,
            observaciones=observaciones
        )

        if aprobado and nivel_sugerido_id:
            nivel_sugerido = Nivel.objects.get(id=nivel_sugerido_id)

            SolicitudPromocion.objects.create(
                nadador=nadador,
                evaluacion=evaluacion,
                nivel_actual=horario.nivel,
                nivel_sugerido=nivel_sugerido
            )

        return redirect('mis_horarios')

    niveles = Nivel.objects.exclude(id=horario.nivel.id)

    return render(request, 'asignaciones/evaluar_nadador.html', {
        'inscripcion': inscripcion,
        'niveles': niveles
    })


@login_required
def solicitudes_pendientes(request):
    solicitudes = SolicitudPromocion.objects.filter(estado='PENDIENTE')
    return render(request, 'asignaciones/solicitudes_pendientes.html', {
        'solicitudes': solicitudes
    })


@login_required
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudPromocion, id=solicitud_id)

    solicitud.estado = 'APROBADA'
    solicitud.autorizado_por = request.user
    solicitud.save()

    inscripcion_actual = InscripcionCarril.objects.filter(
        nadador=solicitud.nadador,
        activo=True
    ).first()

    if inscripcion_actual:
        inscripcion_actual.activo = False
        inscripcion_actual.save()

    nuevo_horario = HorarioCarril.objects.filter(
        nivel=solicitud.nivel_sugerido
    ).first()

    if nuevo_horario:
        InscripcionCarril.objects.create(
            nadador=solicitud.nadador,
            horario_carril=nuevo_horario
        )

    return redirect('solicitudes_pendientes')


@login_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudPromocion, id=solicitud_id)

    if request.method == 'POST':
        motivo = request.POST.get('motivo')

        solicitud.estado = 'RECHAZADA'
        solicitud.motivo_rechazo = motivo
        solicitud.autorizado_por = request.user
        solicitud.save()

        return redirect('solicitudes_pendientes')

    return render(request, 'asignaciones/rechazar_solicitud.html', {
        'solicitud': solicitud
    })