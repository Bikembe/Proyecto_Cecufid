from django.db.models import Count
from django.contrib import messages
import json
from usuarios.decorators import rol_requerido
from .models import EventoCalendario, RecuperacionClase, CupoRecuperacion
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from usuarios.models import Nadador
from asignaciones.models import HorarioCarril, InscripcionCarril
from django.http import JsonResponse
from datetime import datetime

COLORES_NIVEL = {
    "BASICO": "#3498db",
    "INTERMEDIO": "#f1c40f",
    "AVANZADO": "#9b59b6",
    "GENERAL": "#2ecc71"
}


def horarios_disponibles(request):

    fecha = request.GET.get("fecha")

    if EventoCalendario.objects.filter(
        tipo='CANCELACION_DIA',
        fecha=fecha
    ).exists():
        return JsonResponse({
            "cancelado": True,
            "horarios": []
        })

    eventos = EventoCalendario.objects.filter(permite_recuperacion=True)

    if eventos.exists():

        es_valida = False

        for e in eventos:
            if e.fechas_recuperacion:
                try:
                    fechas = [
                        datetime.strptime(f, "%Y-%m-%d").date()
                        for f in e.fechas_recuperacion
                    ]
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                    if fecha_obj in fechas:
                        es_valida = True
                        break
                except:
                    continue

        if not es_valida:
            return JsonResponse({
                "cancelado": False,
                "horarios": [],
                "mensaje": "Fecha no habilitada para recuperación"
            })

    horarios = HorarioCarril.objects.all()
    resultado = []

    for h in horarios:

        if EventoCalendario.objects.filter(
            tipo='CANCELACION_HORARIO',
            fecha=fecha,
            horario_carril=h
        ).exists():
            continue

        nivel = h.nivel

        actuales = RecuperacionClase.objects.filter(
            horario_carril=h,
            fecha=fecha,
            nivel=nivel
        ).count()

        cupo = CupoRecuperacion.objects.filter(
            horario_carril=h,
            nivel=nivel,
            activo=True
        ).first()

        if not cupo:
            continue

        disponibles = cupo.maximo_nadadores - actuales

        if disponibles <= 0:
            continue

        resultado.append({
            "id": h.id,
            "hora_inicio": str(h.hora_inicio),
            "hora_fin": str(h.hora_fin),
            "nivel": nivel,
            "ocupados": actuales,
            "disponibles": disponibles,
            "total": cupo.maximo_nadadores
        })

    return JsonResponse({
        "cancelado": False,
        "horarios": resultado
    })

def api_cupo(request):
    fecha = request.GET.get("fecha")

    cancelado = EventoCalendario.objects.filter(
        tipo='CANCELACION_DIA',
        fecha=fecha
    ).exists()

    return JsonResponse({
        "lleno": False,
        "cancelado": cancelado
    })

@login_required
@rol_requerido(['Recepcion', 'Administrador'])
def recepcion_recuperacion(request):

    nadador = None
    inscripcion = None

    if request.method == "POST":

        if "buscar" in request.POST:

            codigo = request.POST.get("codigo")

            try:
                nadador = Nadador.objects.get(codigo_barras=codigo)

                inscripcion = InscripcionCarril.objects.filter(
                    nadador=nadador,
                    activo=True
                ).select_related('horario_carril').first()

                if not inscripcion:
                    messages.error(request, "El nadador no tiene horario")

            except Nadador.DoesNotExist:
                messages.error(request, "Nadador no encontrado")

        elif "guardar" in request.POST:

            inscripcion = get_object_or_404(
                InscripcionCarril,
                id=request.POST.get("inscripcion_id")
            )

            horario = get_object_or_404(
                HorarioCarril,
                id=request.POST.get("horario_id")
            )

            fecha = request.POST.get("fecha")

            nivel = getattr(inscripcion, "nivel", "GENERAL")

            eventos = EventoCalendario.objects.filter(
                permite_recuperacion=True
            )

            es_valida = False

            try:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            except:
                messages.error(request, "Fecha inválida")
                return redirect("calendario:recepcion_recuperacion")

            for e in eventos:
                if e.fechas_recuperacion:
                    try:
                        fechas = [
                            datetime.strptime(f, "%Y-%m-%d").date()
                            for f in e.fechas_recuperacion
                        ]
                        if fecha_obj in fechas:
                            es_valida = True
                            break
                    except:
                        continue

            if not es_valida:
                messages.error(request, "Fecha no válida para recuperación")
                return redirect("calendario:recepcion_recuperacion")

            if RecuperacionClase.objects.filter(
                inscripcion=inscripcion,
                fecha=fecha
            ).exists():
                messages.error(request, "Ya tiene recuperación ese día")
                return redirect("calendario:recepcion_recuperacion")

            if EventoCalendario.objects.filter(
                tipo='CANCELACION_HORARIO',
                fecha=fecha,
                horario_carril=horario
            ).exists():
                messages.error(request, "Horario cancelado")
                return redirect("calendario:recepcion_recuperacion")

            if EventoCalendario.objects.filter(
                tipo='CANCELACION_DIA',
                fecha=fecha
            ).exists():
                messages.error(request, "Día cancelado")
                return redirect("calendario:recepcion_recuperacion")

            actuales = RecuperacionClase.objects.filter(
                horario_carril=horario,
                fecha=fecha,
                nivel=nivel
            ).count()

            cupo = CupoRecuperacion.objects.filter(
                horario_carril=horario,
                nivel=nivel,
                activo=True
            ).first()

            if not cupo:
                messages.error(request, "Horario sin configuración de cupo")
                return redirect("calendario:recepcion_recuperacion")

            if actuales >= cupo.maximo_nadadores:
                messages.error(request, "Horario lleno")
                return redirect("calendario:recepcion_recuperacion")

            RecuperacionClase.objects.create(
                inscripcion=inscripcion,
                horario_carril=horario,
                fecha=fecha,
                hora_inicio=horario.hora_inicio,
                hora_fin=horario.hora_fin,
                nivel=nivel,
                creado_por=request.user
            )

            messages.success(request, "Recuperación agendada correctamente")
            return redirect("calendario:recepcion_recuperacion")

    return render(request, "calendario/recepcion_recuperacion.html", {
        "nadador": nadador,
        "inscripcion": inscripcion
    })

@login_required
@rol_requerido(['Administrador', 'Coordinador', 'Recepcion'])
def calendario_lista(request):

    eventos = EventoCalendario.objects.all()
    recuperaciones = RecuperacionClase.objects.select_related(
        'inscripcion', 'horario_carril'
    )

    eventos_json = []

    for e in eventos:

        eventos_json.append({
            "title": e.tipo,
            "start": e.fecha.strftime("%Y-%m-%d"),
            "color": "#e74c3c"
        })

        if e.permite_recuperacion and e.fechas_recuperacion:

            for f in e.fechas_recuperacion:

                for h in HorarioCarril.objects.all():

                    if EventoCalendario.objects.filter(
                        tipo='CANCELACION_HORARIO',
                        fecha=f,
                        horario_carril=h
                    ).exists():
                        continue

                    nivel = h.nivel

                    cupo = CupoRecuperacion.objects.filter(
                        horario_carril=h,
                        nivel=nivel,
                        activo=True
                    ).first()

                    if not cupo:
                        continue

                    ocupados = RecuperacionClase.objects.filter(
                        horario_carril=h,
                        fecha=f,
                        nivel=nivel
                    ).count()

                    disponibles = cupo.maximo_nadadores - ocupados

                    if disponibles <= 0:
                        continue

                    color = COLORES_NIVEL.get(nivel.upper(), "#2ecc71")

                    eventos_json.append({
                        "title": f"{nivel} | {h.hora_inicio}-{h.hora_fin} ({disponibles})",
                        "start": f"{f}T{h.hora_inicio}",
                        "end": f"{f}T{h.hora_fin}",
                        "color": color,
                        "extendedProps": {
                            "horario_id": h.id,
                            "nivel": nivel,
                            "disponibles": disponibles
                        }
                    })

    for r in recuperaciones:

        color = COLORES_NIVEL.get(r.nivel.upper(), "#2ecc71")

        eventos_json.append({
            "title": f"{r.nivel} - {r.inscripcion.nadador}",
            "start": f"{r.fecha}T{r.hora_inicio}",
            "end": f"{r.fecha}T{r.hora_fin}",
            "color": color,
            "extendedProps": {
                "horario_id": r.horario_carril.id,
                "tipo": "recuperacion"
            }
        })

    return render(request, "calendario/lista.html", {
        "eventos_json": json.dumps(eventos_json)
    })

@login_required
@rol_requerido(['Administrador', 'Coordinador', 'Recepcion'])
def ocupacion_recuperaciones(request):

    datos = RecuperacionClase.objects.values(
        "horario_carril", "fecha", "nivel"
    ).annotate(total=Count("id"))

    return render(request, "calendario/ocupacion.html", {
        "datos": datos
    })

@login_required
@rol_requerido(['Administrador', 'Coordinador'])
def cancelar_dia(request):

    if request.method == "POST":

        EventoCalendario.objects.create(
            tipo='CANCELACION_DIA',
            fecha=request.POST.get("fecha"),
            motivo=request.POST.get("motivo"),
            creado_por=request.user,
            permite_recuperacion=request.POST.get("permite_recuperacion") == "on",
            fechas_recuperacion=request.POST.getlist("fechas_recuperacion")
        )

        messages.success(request, "Día cancelado")
        return redirect("calendario:calendario_lista")

    return render(request, "calendario/cancelar_dia.html")


@login_required
@rol_requerido(['Administrador', 'Coordinador'])
def cancelar_horario(request):

    horarios = HorarioCarril.objects.all()

    if request.method == "POST":

        horario = get_object_or_404(
            HorarioCarril,
            id=request.POST.get("horario")
        )

        EventoCalendario.objects.create(
            tipo='CANCELACION_HORARIO',
            horario_carril=horario,
            fecha=request.POST.get("fecha"),
            motivo=request.POST.get("motivo"),
            creado_por=request.user,
            permite_recuperacion=request.POST.get("permite_recuperacion") == "on",
            fechas_recuperacion=request.POST.getlist("fechas_recuperacion")
        )

        messages.success(request, "Horario cancelado")
        return redirect("calendario:calendario_lista")

    return render(request, "calendario/cancelar_horario.html", {
        "horarios": horarios
    })


@login_required
def detalle_horario(request):

    fecha = request.GET.get("fecha")
    horario_id = request.GET.get("horario")

    horario = get_object_or_404(HorarioCarril, id=horario_id)

    nivel = horario.nivel

    cupo = CupoRecuperacion.objects.filter(
        horario_carril=horario,
        nivel=nivel,
        activo=True
    ).first()

    ocupados = RecuperacionClase.objects.filter(
        horario_carril=horario,
        fecha=fecha,
        nivel=nivel
    ).count()

    disponibles = 0
    if cupo:
        disponibles = cupo.maximo_nadadores - ocupados

    return JsonResponse({
        "nivel": nivel,
        "hora_inicio": str(horario.hora_inicio),
        "hora_fin": str(horario.hora_fin),
        "ocupados": ocupados,
        "disponibles": disponibles
    })

@login_required
def agendar_desde_calendario(request):

    if request.method == "POST":

        inscripcion_id = request.POST.get("inscripcion")
        horario_id = request.POST.get("horario")
        fecha = request.POST.get("fecha")

        inscripcion = get_object_or_404(InscripcionCarril, id=inscripcion_id)
        horario = get_object_or_404(HorarioCarril, id=horario_id)

        nivel = getattr(inscripcion, "nivel", "GENERAL")

        if RecuperacionClase.objects.filter(
            inscripcion=inscripcion,
            fecha=fecha
        ).exists():
            return JsonResponse({"error": "Ya tiene recuperación"})

        actuales = RecuperacionClase.objects.filter(
            horario_carril=horario,
            fecha=fecha,
            nivel=nivel
        ).count()

        cupo = CupoRecuperacion.objects.filter(
            horario_carril=horario,
            nivel=nivel,
            activo=True
        ).first()

        if not cupo or actuales >= cupo.maximo_nadadores:
            return JsonResponse({"error": "Sin cupo"})

        RecuperacionClase.objects.create(
            inscripcion=inscripcion,
            horario_carril=horario,
            fecha=fecha,
            hora_inicio=horario.hora_inicio,
            hora_fin=horario.hora_fin,
            nivel=nivel,
            creado_por=request.user
        )

        return JsonResponse({"success": True})