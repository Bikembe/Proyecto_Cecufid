from django.shortcuts import render, redirect, get_object_or_404
from datetime import date

from .models import PreRegistro
from asignaciones.models import HorarioCarril, InscripcionCarril, Nivel
from reportes.utils import registrar_accion

from usuarios.decorators import rol_requerido


def calcular_edad(fecha_nacimiento):
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year

    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1

    return edad


@rol_requerido(['Administrador', 'Recepcion'])
def detalle_preregistro(request, pk):

    preregistro = get_object_or_404(PreRegistro, pk=pk)

    registrar_accion(
        usuario=request.user if request.user.is_authenticated else None,
        modulo="PRE_REGISTRO",
        accion="CONSULTA",
        descripcion=f"Consultó preregistro {preregistro.folio}",
        request=request
    )

    return render(request, "preregistro/detalle.html", {
        "preregistro": preregistro,
        "codigo": preregistro.folio
    })


@rol_requerido(['Administrador', 'Recepcion'])
def crear_preregistro(request):

    niveles = Nivel.objects.all()

    horarios_qs = HorarioCarril.objects.select_related("carril", "nivel", "maestro")

    horarios = []

    for h in horarios_qs:
        ocupados = InscripcionCarril.objects.filter(
            horario_carril=h,
            activo=True
        ).count()

        disponibles = h.capacidad_maxima - ocupados

        if disponibles > 0:
            horarios.append({
                "id": h.id,
                "nivel": h.nivel.id,
                "dias": h.dias,
                "texto": f"{h.carril} | {h.hora_inicio} - {h.hora_fin}",
                "disponibles": disponibles
            })

    if request.method == "POST":

        fecha_nacimiento = request.POST.get("fecha_nacimiento")
        horario_id = request.POST.get("horario")
        horario_sabado_id = request.POST.get("horario_sabado")

        if not fecha_nacimiento or not horario_id:
            return render(request, "preregistro/form.html", {
                "horarios": horarios,
                "niveles": niveles,
                "error": "Datos incompletos"
            })

        fecha_nacimiento = date.fromisoformat(fecha_nacimiento)

        es_menor = request.POST.get("tutor_nombre") not in [None, ""]

        if es_menor:
            foto = request.FILES.get("foto_menor")
            acta = request.FILES.get("acta_nacimiento")
            curp_doc = request.FILES.get("curp")
            identificacion = request.FILES.get("ine_tutor")

            if not foto or not acta or not curp_doc or not identificacion:
                return render(request, "preregistro/form.html", {
                    "horarios": horarios,
                    "niveles": niveles,
                    "error": "Faltan documentos del menor o tutor"
                })

        else:
            foto = request.FILES.get("foto")
            identificacion = request.FILES.get("identificacion")
            acta = None
            curp_doc = None

            if not foto or not identificacion:
                return render(request, "preregistro/form.html", {
                    "horarios": horarios,
                    "niveles": niveles,
                    "error": "Faltan documentos del adulto"
                })

        preregistro = PreRegistro.objects.create(

            nombre=request.POST.get("nombre"),
            apellido_paterno=request.POST.get("apellido_paterno"),
            apellido_materno=request.POST.get("apellido_materno"),
            fecha_nacimiento=fecha_nacimiento,
            sexo=request.POST.get("sexo"),
            telefono=request.POST.get("telefono"),
            correo=request.POST.get("correo"),

            foto=foto,
            acta_nacimiento=acta,
            curp_documento=curp_doc,
            identificacion=identificacion,

            categoria_id=request.POST.get("nivel"),
            plan_id=horario_id,
            dias_seleccionados=request.POST.get("dias_seleccionados"),

            contacto_emergencia_nombre=request.POST.get("emergencia_nombre"),
            contacto_emergencia_telefono=request.POST.get("emergencia_tel"),
            contacto_emergencia_trabajo=request.POST.get("emergencia_trabajo"),
            contacto_emergencia_parentesco=request.POST.get("emergencia_parentesco"),

            acepta_terminos=True,
            estado="PENDIENTE_EXAMEN"
        )

        registrar_accion(
            usuario=request.user if request.user.is_authenticated else None,
            modulo="PRE_REGISTRO",
            accion="CREAR",
            descripcion=f"Creó preregistro {preregistro.folio}",
            request=request
        )

        return redirect("preregistro:detalle", preregistro.id)

    registrar_accion(
        usuario=request.user if request.user.is_authenticated else None,
        modulo="PRE_REGISTRO",
        accion="CONSULTA",
        descripcion="Acceso al formulario de preregistro",
        request=request
    )

    return render(request, "preregistro/form.html", {
        "horarios": horarios,
        "niveles": niveles
    })