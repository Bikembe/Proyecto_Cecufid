from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from datetime import date

from usuarios.decorators import rol_requerido
from preregistro.models import PreRegistro
from usuarios.models import Nadador, Inscripcion
from asignaciones.models import HorarioCarril, InscripcionCarril
from pagos.models import Pago, Tarifa, Descuento


# =========================
# 🔹 ESCANEAR
# =========================
@login_required
@rol_requerido(['Administrador', 'Caja'])
def escanear_pago(request):

    preregistro = None
    mensaje = None

    if request.method == "POST":
        folio = request.POST.get("folio")

        try:
            preregistro = PreRegistro.objects.get(folio=folio)
        except PreRegistro.DoesNotExist:
            mensaje = "Folio no encontrado"

    return render(request, "pagos/escanear.html", {
        "preregistro": preregistro,
        "mensaje": mensaje
    })


# =========================
# 🔹 FUNCIONES AUXILIARES
# =========================
def calcular_recargo():
    hoy = date.today()
    dia = hoy.day

    if dia > 5:
        return (dia - 5) * 10  # $10 por día
    return 0


def verificar_pago_mes(inscripcion):
    hoy = date.today()

    return Pago.objects.filter(
        inscripcion=inscripcion,
        tipo_pago="MENSUALIDAD",
        fecha_pago__month=hoy.month,
        fecha_pago__year=hoy.year
    ).exists()


def meses_adeudo(inscripcion):
    hoy = date.today()

    pagos = Pago.objects.filter(
        inscripcion=inscripcion,
        tipo_pago="MENSUALIDAD"
    ).order_by("-fecha_pago")

    if not pagos.exists():
        return 999  # nunca ha pagado

    ultimo_pago = pagos.first().fecha_pago

    diferencia = (hoy.year - ultimo_pago.year) * 12 + (hoy.month - ultimo_pago.month)

    return diferencia


# =========================
# 🔹 PROCESAR PAGO
# =========================
@login_required
@rol_requerido(['Administrador', 'Caja'])
@transaction.atomic
def procesar_pago(request, preregistro_id):

    preregistro = get_object_or_404(PreRegistro, id=preregistro_id)

    # 🔹 DIAS DESDE PREREGISTRO
    dias = [d.strip() for d in preregistro.dias_seleccionados.split(",") if d.strip()]
    total_dias = len(dias)

    tarifa_mensual = Tarifa.objects.filter(
        tipo="MENSUALIDAD",
        dias=total_dias,
        activo=True
    ).first()

    if not tarifa_mensual:
        messages.error(request, f"No hay tarifa para {total_dias} días")
        return redirect("pagos:escanear_pago")

    tarifa_inscripcion = Tarifa.objects.filter(tipo="INSCRIPCION", activo=True).first()
    tarifa_examen = Tarifa.objects.filter(tipo="EXAMEN", activo=True).first()

    monto_mensual = tarifa_mensual.monto
    monto_inscripcion = tarifa_inscripcion.monto if tarifa_inscripcion else 0
    monto_examen = tarifa_examen.monto if tarifa_examen else 0

    # 🔹 DESCUENTO DINAMICO
    descuento_id = request.POST.get("descuento")
    descuento_aplicado = 0

    if descuento_id:
        descuento = Descuento.objects.get(id=descuento_id)
        subtotal = monto_mensual + monto_inscripcion
        descuento_aplicado = subtotal * (descuento.porcentaje / 100)

    # 🔹 RECARGO
    recargo = calcular_recargo()

    total = (monto_mensual + monto_inscripcion + monto_examen + recargo) - descuento_aplicado

    # =========================
    # 🔥 POST
    # =========================
    if request.method == "POST":

        if preregistro.estado != "APTO":
            messages.error(request, "No apto")
            return redirect("pagos:escanear_pago")

        horario = get_object_or_404(HorarioCarril, id=preregistro.plan_id)

        # 🔹 VALIDAR CUPO
        ocupados = InscripcionCarril.objects.filter(
            horario_carril=horario,
            activo=True
        ).count()

        if ocupados >= horario.capacidad_maxima:
            messages.error(request, "Horario lleno")
            return redirect("pagos:escanear_pago")

        # 🔹 CREAR NADADOR
        nadador, _ = Nadador.objects.get_or_create(
            codigo_barras=preregistro.folio,
            defaults={
                "nombre": preregistro.nombre,
                "apellido_paterno": preregistro.apellido_paterno,
                "apellido_materno": preregistro.apellido_materno,
                "fecha_nacimiento": preregistro.fecha_nacimiento,
                "sexo": preregistro.sexo,
                "telefono": preregistro.telefono,
                "correo": preregistro.correo,
                "estado": "activo"
            }
        )

        # 🔹 INSCRIPCION
        inscripcion, _ = Inscripcion.objects.get_or_create(
            nadador=nadador,
            defaults={"plan_id": preregistro.plan_id}
        )

        # 🔹 VALIDAR ADEUDO
        deuda = meses_adeudo(inscripcion)

        if deuda >= 3:
            # 🔴 BAJA AUTOMATICA (solo inscripción)
            inscripcion.delete()
            messages.error(request, "Baja automática por adeudo de 3 meses")
            return redirect("pagos:escanear_pago")

        # 🔹 VALIDAR SI YA PAGÓ
        if verificar_pago_mes(inscripcion):
            messages.warning(request, "Ya pagó este mes")
            return redirect("pagos:escanear_pago")

        # 🔹 CREAR PAGOS
        Pago.objects.create(
            inscripcion=inscripcion,
            tipo_pago="MENSUALIDAD",
            monto=monto_mensual + recargo,
            metodo_pago=request.POST.get("metodo"),
            referencia=request.POST.get("referencia"),
        )

        if monto_inscripcion > 0:
            Pago.objects.create(
                preregistro=preregistro,
                tipo_pago="INSCRIPCION",
                monto=monto_inscripcion,
                metodo_pago=request.POST.get("metodo"),
            )

        if monto_examen > 0:
            Pago.objects.create(
                preregistro=preregistro,
                tipo_pago="EXAMEN",
                monto=monto_examen,
                metodo_pago=request.POST.get("metodo"),
            )

        # 🔹 ASIGNAR CARRIL
        InscripcionCarril.objects.get_or_create(
            nadador=nadador,
            horario_carril=horario,
            defaults={"activo": True}
        )

        preregistro.estado = "INSCRITO"
        preregistro.save()

        messages.success(request, "Pago completado correctamente")
        return redirect("pagos:escanear_pago")

    descuentos = Descuento.objects.all()

    return render(request, "pagos/procesar.html", {
        "preregistro": preregistro,
        "monto_mensual": monto_mensual,
        "monto_inscripcion": monto_inscripcion,
        "monto_examen": monto_examen,
        "recargo": recargo,
        "descuento": descuento_aplicado,
        "total": total,
        "descuentos": descuentos
    })


# =========================
# 🔹 CRUD TARIFAS
# =========================
@login_required
@rol_requerido(['Administrador'])
def tarifa_lista(request):
    tarifas = Tarifa.objects.all()
    return render(request, "pagos/tarifa_lista.html", {"tarifas": tarifas})


@login_required
@rol_requerido(['Administrador'])
def tarifa_crear(request):

    if request.method == "POST":
        Tarifa.objects.create(
            nombre=request.POST.get("nombre"),
            tipo=request.POST.get("tipo"),
            dias=request.POST.get("dias") or None,
            monto=request.POST.get("monto"),
            activo=True
        )
        return redirect("pagos:tarifa_lista")

    return render(request, "pagos/tarifa_form.html")


@login_required
@rol_requerido(['Administrador'])
def tarifa_editar(request, pk):

    tarifa = get_object_or_404(Tarifa, pk=pk)

    if request.method == "POST":
        tarifa.nombre = request.POST.get("nombre")
        tarifa.tipo = request.POST.get("tipo")
        tarifa.dias = request.POST.get("dias") or None
        tarifa.monto = request.POST.get("monto")
        tarifa.activo = 'activo' in request.POST
        tarifa.save()

        return redirect("pagos:tarifa_lista")

    return render(request, "pagos/tarifa_form.html", {"tarifa": tarifa})


@login_required
@rol_requerido(['Administrador'])
def tarifa_eliminar(request, pk):
    tarifa = get_object_or_404(Tarifa, pk=pk)
    tarifa.delete()
    return redirect("pagos:tarifa_lista")