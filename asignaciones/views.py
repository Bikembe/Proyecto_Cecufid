from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from datetime import date

from .models import (
    Alberca, Carril, Curso, Grupo, Asignacion,
    Inscripcion, Nivel, HorarioCarril, Usuario, Nadador
)


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

def dashboard(request):
    context = {
        'total_carriles': Carril.objects.count(),
        'carriles_disponibles': Carril.objects.filter(estado='disponible').count(),
        'carriles_ocupados': Carril.objects.filter(estado='ocupado').count(),
        'total_grupos': Grupo.objects.filter(activo=True).count(),
        'total_asignaciones': Asignacion.objects.filter(activa=True).count(),
        'grupos_recientes': Grupo.objects.filter(activo=True).select_related(
            'curso', 'entrenador', 'carril'
        ).order_by('-created_at')[:5],
    }
    return render(request, 'asignaciones/dashboard.html', context)


# ─────────────────────────────────────────────
#  CARRILES
# ─────────────────────────────────────────────

def carril_lista(request):
    alberca_id = request.GET.get('alberca')
    carriles = Carril.objects.select_related('alberca').all()
    if alberca_id:
        carriles = carriles.filter(alberca_id=alberca_id)
    return render(request, 'asignaciones/carril_lista.html', {
        'carriles': carriles,
        'albercas': Alberca.objects.all(),
        'alberca_seleccionada': alberca_id,
    })


def carril_crear(request):
    albercas = Alberca.objects.all()
    if request.method == 'POST':
        alberca_id = request.POST.get('alberca')
        numero = request.POST.get('numero')
        if Carril.objects.filter(alberca_id=alberca_id, numero=numero).exists():
            messages.error(request, f'Ya existe el Carril {numero} en esa alberca.')
            return render(request, 'asignaciones/carril_form.html', {'albercas': albercas, 'accion': 'Crear'})
        Carril.objects.create(
            alberca_id=alberca_id,
            numero=numero,
            profundidad=request.POST.get('profundidad') or None,
            capacidad_usuarios=request.POST.get('capacidad_usuarios'),
            estado=request.POST.get('estado', 'disponible'),
        )
        messages.success(request, f'Carril {numero} creado.')
        return redirect('asignaciones:carril_lista')
    return render(request, 'asignaciones/carril_form.html', {'albercas': albercas, 'accion': 'Crear'})


def carril_editar(request, pk):
    carril = get_object_or_404(Carril, pk=pk)
    if request.method == 'POST':
        carril.alberca_id = request.POST.get('alberca')
        carril.numero = request.POST.get('numero')
        carril.profundidad = request.POST.get('profundidad') or None
        carril.capacidad_usuarios = request.POST.get('capacidad_usuarios')
        carril.estado = request.POST.get('estado')
        carril.save()
        messages.success(request, 'Carril actualizado.')
        return redirect('asignaciones:carril_lista')
    return render(request, 'asignaciones/carril_form.html', {
        'carril': carril,
        'albercas': Alberca.objects.all(),
        'accion': 'Editar',
    })


def carril_eliminar(request, pk):
    carril = get_object_or_404(Carril, pk=pk)
    if request.method == 'POST':
        num = carril.numero
        carril.delete()
        messages.success(request, f'Carril {num} eliminado.')
        return redirect('asignaciones:carril_lista')
    return render(request, 'asignaciones/confirmar_eliminar.html', {
        'objeto': f'Carril {carril.numero}',
        'cancelar_url': 'asignaciones:carril_lista',
    })


# ─────────────────────────────────────────────
#  HORARIOS DE CARRIL (tabla real de la BD)
# ─────────────────────────────────────────────

def horario_lista(request):
    horarios = HorarioCarril.objects.select_related('carril__alberca', 'nivel', 'maestro').all()
    return render(request, 'asignaciones/horario_lista.html', {'horarios': horarios})


def horario_crear(request):
    context = {
        'carriles': Carril.objects.select_related('alberca').all(),
        'niveles': Nivel.objects.all(),
        'maestros': Usuario.objects.all(),
        'accion': 'Crear',
    }
    if request.method == 'POST':
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        if hora_fin <= hora_inicio:
            messages.error(request, 'La hora de fin debe ser mayor a la de inicio.')
            return render(request, 'asignaciones/horario_form.html', context)

        nuevo = HorarioCarril(
            carril_id=request.POST.get('carril'),
            nivel_id=request.POST.get('nivel'),
            maestro_id=request.POST.get('maestro'),
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            capacidad_maxima=request.POST.get('capacidad_maxima'),
        )
        if nuevo.hay_choque_maestro():
            messages.error(request, '⚠️ El maestro ya tiene una clase en ese horario.')
            return render(request, 'asignaciones/horario_form.html', context)
        if nuevo.hay_choque_carril():
            messages.error(request, '⚠️ El carril ya está ocupado en ese horario.')
            return render(request, 'asignaciones/horario_form.html', context)

        nuevo.save()
        # Marcar carril como ocupado
        carril = Carril.objects.get(pk=nuevo.carril_id)
        if carril.estado == 'disponible':
            carril.estado = 'ocupado'
            carril.save()

        messages.success(request, 'Horario creado correctamente.')
        return redirect('asignaciones:horario_lista')
    return render(request, 'asignaciones/horario_form.html', context)


def horario_editar(request, pk):
    horario = get_object_or_404(HorarioCarril, pk=pk)
    context = {
        'horario': horario,
        'carriles': Carril.objects.select_related('alberca').all(),
        'niveles': Nivel.objects.all(),
        'maestros': Usuario.objects.all(),
        'accion': 'Editar',
    }
    if request.method == 'POST':
        horario.carril_id = request.POST.get('carril')
        horario.nivel_id = request.POST.get('nivel')
        horario.maestro_id = request.POST.get('maestro')
        horario.hora_inicio = request.POST.get('hora_inicio')
        horario.hora_fin = request.POST.get('hora_fin')
        horario.capacidad_maxima = request.POST.get('capacidad_maxima')

        if horario.hora_fin <= horario.hora_inicio:
            messages.error(request, 'La hora de fin debe ser mayor a la de inicio.')
            return render(request, 'asignaciones/horario_form.html', context)
        if horario.hay_choque_maestro():
            messages.error(request, '⚠️ El maestro ya tiene una clase en ese horario.')
            return render(request, 'asignaciones/horario_form.html', context)
        if horario.hay_choque_carril():
            messages.error(request, '⚠️ El carril ya está ocupado en ese horario.')
            return render(request, 'asignaciones/horario_form.html', context)

        horario.save()
        messages.success(request, 'Horario actualizado.')
        return redirect('asignaciones:horario_lista')
    return render(request, 'asignaciones/horario_form.html', context)


def horario_eliminar(request, pk):
    horario = get_object_or_404(HorarioCarril, pk=pk)
    if request.method == 'POST':
        horario.delete()
        messages.success(request, 'Horario eliminado.')
        return redirect('asignaciones:horario_lista')
    return render(request, 'asignaciones/confirmar_eliminar.html', {
        'objeto': str(horario),
        'cancelar_url': 'asignaciones:horario_lista',
    })


# ─────────────────────────────────────────────
#  CUADRÍCULA (usa HorarioCarril)
# ─────────────────────────────────────────────

def asignacion_cuadricula(request):
    alberca_id = request.GET.get('alberca')
    albercas = Alberca.objects.all()
    carriles = Carril.objects.select_related('alberca').all()
    if alberca_id:
        carriles = carriles.filter(alberca_id=alberca_id)

    horarios = HorarioCarril.objects.select_related(
        'carril', 'maestro', 'nivel'
    ).all()
    if alberca_id:
        horarios = horarios.filter(carril__alberca_id=alberca_id)

    return render(request, 'asignaciones/cuadricula.html', {
        'carriles': carriles,
        'horarios': horarios,
        'albercas': albercas,
        'alberca_seleccionada': alberca_id,
    })


# ─────────────────────────────────────────────
#  GRUPOS
# ─────────────────────────────────────────────

def grupo_lista(request):
    grupos = Grupo.objects.filter(activo=True).select_related('curso', 'entrenador', 'alberca', 'carril')
    return render(request, 'asignaciones/grupo_lista.html', {'grupos': grupos})


def grupo_crear(request):
    context = {
        'cursos': Curso.objects.all(),
        'albercas': Alberca.objects.all(),
        'carriles': Carril.objects.select_related('alberca').all(),
        'entrenadores': Usuario.objects.all(),
        'turnos': Grupo.TURNO_CHOICES,
        'accion': 'Crear',
    }
    if request.method == 'POST':
        Grupo.objects.create(
            curso_id=request.POST.get('curso'),
            alberca_id=request.POST.get('alberca'),
            carril_id=request.POST.get('carril') or None,
            entrenador_id=request.POST.get('entrenador'),
            cupo_maximo=request.POST.get('cupo_maximo'),
            turno=request.POST.get('turno'),
        )
        messages.success(request, 'Grupo creado.')
        return redirect('asignaciones:grupo_lista')
    return render(request, 'asignaciones/grupo_form.html', context)


def grupo_editar(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    context = {
        'grupo': grupo,
        'cursos': Curso.objects.all(),
        'albercas': Alberca.objects.all(),
        'carriles': Carril.objects.select_related('alberca').all(),
        'entrenadores': Usuario.objects.all(),
        'turnos': Grupo.TURNO_CHOICES,
        'accion': 'Editar',
    }
    if request.method == 'POST':
        grupo.curso_id = request.POST.get('curso')
        grupo.alberca_id = request.POST.get('alberca')
        grupo.carril_id = request.POST.get('carril') or None
        grupo.entrenador_id = request.POST.get('entrenador')
        grupo.cupo_maximo = request.POST.get('cupo_maximo')
        grupo.turno = request.POST.get('turno')
        grupo.save()
        messages.success(request, 'Grupo actualizado.')
        return redirect('asignaciones:grupo_lista')
    return render(request, 'asignaciones/grupo_form.html', context)


def grupo_detalle(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    inscripciones = grupo.inscripciones.select_related('nadador').filter(estado='activo')
    return render(request, 'asignaciones/grupo_detalle.html', {
        'grupo': grupo,
        'inscripciones': inscripciones,
    })


def grupo_eliminar(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    if request.method == 'POST':
        grupo.activo = False
        grupo.save()
        messages.success(request, 'Grupo desactivado.')
        return redirect('asignaciones:grupo_lista')
    return render(request, 'asignaciones/confirmar_eliminar.html', {
        'objeto': str(grupo),
        'cancelar_url': 'asignaciones:grupo_lista',
    })


# ─────────────────────────────────────────────
#  INSCRIPCIONES
# ─────────────────────────────────────────────

def inscripcion_crear(request, grupo_pk):
    grupo = get_object_or_404(Grupo, pk=grupo_pk)
    if not grupo.hay_cupo():
        messages.error(request, 'El grupo ya alcanzó su cupo máximo.')
        return redirect('asignaciones:grupo_detalle', pk=grupo_pk)

    inscritos_ids = grupo.inscripciones.values_list('nadador_id', flat=True)
    nadadores = Nadador.objects.all().exclude(id__in=inscritos_ids)

    if request.method == 'POST':
        Inscripcion.objects.create(
            nadador_id=request.POST.get('nadador'),
            grupo=grupo,
            fecha_inscripcion=date.today(),
            estado='activo',
        )
        messages.success(request, 'Nadador inscrito.')
        return redirect('asignaciones:grupo_detalle', pk=grupo_pk)

    return render(request, 'asignaciones/inscripcion_form.html', {
        'grupo': grupo,
        'nadadores': nadadores,
    })


def inscripcion_baja(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    grupo_pk = inscripcion.grupo_id
    if request.method == 'POST':
        inscripcion.estado = 'inactivo'
        inscripcion.save()
        messages.success(request, 'Inscripción dada de baja.')
    return redirect('asignaciones:grupo_detalle', pk=grupo_pk)


# ─────────────────────────────────────────────
#  REPORTES
# ─────────────────────────────────────────────

def reporte_uso_carriles(request):
    carriles = Carril.objects.select_related('alberca').all()
    maestros_stats = []
    for u in Usuario.objects.all():
        horarios = HorarioCarril.objects.filter(maestro=u)
        horas = sum(
            (h.hora_fin.hour * 60 + h.hora_fin.minute) -
            (h.hora_inicio.hour * 60 + h.hora_inicio.minute)
            for h in horarios
        ) / 60
        if horarios.count() > 0:
            maestros_stats.append({
                'entrenador': u,
                'num_asignaciones': horarios.count(),
                'horas_semanales': round(horas, 1),
            })

    return render(request, 'asignaciones/reporte.html', {
        'carriles': carriles,
        'maestros_stats': maestros_stats,
        'hoy': date.today(),
    })


# ─────────────────────────────────────────────
#  API JSON
# ─────────────────────────────────────────────

def api_carriles_por_alberca(request, alberca_id):
    carriles = Carril.objects.filter(alberca_id=alberca_id).values(
        'id', 'numero', 'estado', 'capacidad_usuarios'
    )
    return JsonResponse(list(carriles), safe=False)