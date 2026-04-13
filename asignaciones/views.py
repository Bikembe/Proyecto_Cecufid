from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Carril, HorarioCarril, InscripcionCarril, Nivel
from usuarios.models import Usuario, Nadador

# ==============================
# DASHBOARD
# ==============================
@login_required
def dashboard(request):
    total_carriles = Carril.objects.count()
    total_horarios = HorarioCarril.objects.count()
    total_inscripciones = InscripcionCarril.objects.filter(activo=True).count()

    return render(request, "asignaciones/dashboard.html", {
        "total_carriles": total_carriles,
        "total_horarios": total_horarios,
        "total_inscripciones": total_inscripciones
    })


# ==============================
# CARRILES
# ==============================
@login_required
def carril_lista(request):
    carriles = Carril.objects.all()
    return render(request, "asignaciones/carril_lista.html", {
        "carriles": carriles
    })


@login_required
def carril_crear(request):
    if request.method == "POST":
        numero = request.POST.get("numero")

        Carril.objects.create(numero=numero)
        messages.success(request, "Carril creado correctamente")
        return redirect("asignaciones:carril_lista")

    return render(request, "asignaciones/carril_form.html")


@login_required
def carril_editar(request, pk):
    carril = get_object_or_404(Carril, pk=pk)

    if request.method == "POST":
        carril.numero = request.POST.get("numero")
        carril.save()
        messages.success(request, "Carril actualizado")
        return redirect("asignaciones:carril_lista")

    return render(request, "asignaciones/carril_form.html", {
        "carril": carril
    })


@login_required
def carril_eliminar(request, pk):
    carril = get_object_or_404(Carril, pk=pk)
    carril.delete()
    messages.success(request, "Carril eliminado")
    return redirect("asignaciones:carril_lista")


# ==============================
# HORARIOS (CLAVE DEL SISTEMA)
# ==============================
@login_required
def horario_lista(request):
    horarios = HorarioCarril.objects.select_related('carril', 'nivel', 'maestro')

    return render(request, "asignaciones/horario_lista.html", {
        "horarios": horarios
    })


@login_required
def horario_crear(request):
    carriles = Carril.objects.all()
    niveles = Nivel.objects.all()
    maestros = Usuario.objects.filter(rol__nombre__iexact="maestro")

    if request.method == "POST":
        carril_id = request.POST.get("carril")
        nivel_id = request.POST.get("nivel")
        maestro_id = request.POST.get("maestro")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")
        capacidad = request.POST.get("capacidad")

        horario = HorarioCarril(
            carril_id=carril_id,
            nivel_id=nivel_id,
            maestro_id=maestro_id,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            capacidad_maxima=capacidad
        )

        try:
            horario.save()
            messages.success(request, "Horario creado correctamente")
            return redirect("asignaciones:horario_lista")
        except Exception as e:
            messages.error(request, str(e))

    return render(request, "asignaciones/horario_form.html", {
        "carriles": carriles,
        "niveles": niveles,
        "maestros": maestros
    })


@login_required
def horario_editar(request, pk):
    horario = get_object_or_404(HorarioCarril, pk=pk)

    carriles = Carril.objects.all()
    niveles = Nivel.objects.all()
    maestros = Usuario.objects.filter(rol__nombre__iexact="maestro")

    if request.method == "POST":
        horario.carril_id = request.POST.get("carril")
        horario.nivel_id = request.POST.get("nivel")
        horario.maestro_id = request.POST.get("maestro")
        horario.hora_inicio = request.POST.get("hora_inicio")
        horario.hora_fin = request.POST.get("hora_fin")
        horario.capacidad_maxima = request.POST.get("capacidad")

        try:
            horario.save()
            messages.success(request, "Horario actualizado")
            return redirect("asignaciones:horario_lista")
        except Exception as e:
            messages.error(request, str(e))

    return render(request, "asignaciones/horario_form.html", {
        "horario": horario,
        "carriles": carriles,
        "niveles": niveles,
        "maestros": maestros
    })


@login_required
def horario_eliminar(request, pk):
    horario = get_object_or_404(HorarioCarril, pk=pk)
    horario.delete()
    messages.success(request, "Horario eliminado")
    return redirect("asignaciones:horario_lista")


# ==============================
# CUADRÍCULA VISUAL
# ==============================
@login_required
def asignacion_cuadricula(request):
    horarios = HorarioCarril.objects.select_related('carril', 'maestro', 'nivel').order_by('hora_inicio')

    return render(request, "asignaciones/cuadricula.html", {
        "horarios": horarios
    })


# ==============================
# REPORTE
# ==============================
@login_required
def reporte_uso_carriles(request):
    horarios = HorarioCarril.objects.all()

    data = []
    for h in horarios:
        ocupados = InscripcionCarril.objects.filter(horario_carril=h, activo=True).count()

        data.append({
            "horario": h,
            "ocupados": ocupados,
            "disponibles": h.capacidad_maxima - ocupados
        })

    return render(request, "asignaciones/reporte.html", {
        "data": data
    })

@login_required
def grupo_detalle(request, pk):
    horario = get_object_or_404(HorarioCarril, pk=pk)

    inscripciones = InscripcionCarril.objects.filter(
        horario_carril=horario,
        activo=True
    )

    return render(request, "asignaciones/grupo_detalle.html", {
        "horario": horario,
        "inscripciones": inscripciones
    })

@login_required
def inscribir_nadador(request, pk):
    horario = get_object_or_404(HorarioCarril, pk=pk)

    if request.method == "POST":
        nadador_id = request.POST.get("nadador")

        InscripcionCarril.objects.create(
            nadador_id=nadador_id,
            horario_carril=horario
        )

        messages.success(request, "Nadador inscrito")
        return redirect("asignaciones:grupo_detalle", pk=pk)

    return render(request, "asignaciones/inscribir.html", {
        "horario": horario
    })

# ==============================
# LISTA DE INSCRIPCIONES
# ==============================
@login_required
def inscripcion_lista(request):
    inscripciones = InscripcionCarril.objects.select_related(
        'nadador', 'horario_carril'
    )

    return render(request, "asignaciones/inscripcion_lista.html", {
        "inscripciones": inscripciones
    })


# ==============================
# CREAR INSCRIPCIÓN
# ==============================
@login_required
def inscripcion_crear(request):
    nadadores = Nadador.objects.all()
    horarios = []
    maestros = Usuario.objects.filter(rol__nombre="Maestro")

    # 🔹 ESTE FOR VA DENTRO DE LA FUNCIÓN
    for h in HorarioCarril.objects.all():
        ocupados = InscripcionCarril.objects.filter(
            horario_carril=h,
            activo=True
        ).count()

        disponibles = h.capacidad_maxima - ocupados

        horarios.append({
            "id": h.id,
            "texto": f"{h.carril} | {h.hora_inicio} - {h.hora_fin}",
            "disponibles": disponibles
        })

    # 🔹 ESTO TAMBIÉN VA DENTRO
    if request.method == "POST":
        nadador_id = request.POST.get("nadador")
        horario_id = request.POST.get("horario")

        inscripcion = InscripcionCarril(
            nadador_id=nadador_id,
            horario_carril_id=horario_id
        )

        try:
            inscripcion.save()
            messages.success(request, "Inscripción realizada correctamente")
            return redirect("asignaciones:inscripcion_lista")
        except Exception as e:
            messages.error(request, str(e))

    return render(request, "asignaciones/inscripcion_form.html", {
        "nadadores": nadadores,
        "horarios": horarios,
        "maestros": maestros
    })


# ==============================
# DAR DE BAJA (soft delete)
# ==============================
@login_required
def inscripcion_baja(request, pk):
    inscripcion = get_object_or_404(InscripcionCarril, pk=pk)
    inscripcion.activo = False
    inscripcion.save()

    messages.success(request, "Inscripción dada de baja")
    return redirect("asignaciones:inscripcion_lista")

from django.http import JsonResponse

@login_required
def api_horarios(request):
    maestro_id = request.GET.get("maestro")

    horarios_qs = HorarioCarril.objects.all()

    # 🔹 FILTRO
    if maestro_id:
        horarios_qs = horarios_qs.filter(maestro_id=maestro_id)

    data = []

    for h in horarios_qs:
        ocupados = InscripcionCarril.objects.filter(
            horario_carril=h,
            activo=True
        ).count()

        disponibles = h.capacidad_maxima - ocupados

        data.append({
            "id": h.id,
            "texto": f"{h.carril} | {h.hora_inicio} - {h.hora_fin} | {h.maestro}",
            "disponibles": disponibles
        })

    return JsonResponse(data, safe=False)

@login_required
def nivel_crear(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")

        Nivel.objects.create(
            nombre=nombre,
            descripcion=descripcion
        )

        return redirect("asignaciones:horario_crear")

    return render(request, "asignaciones/nivel_form.html")