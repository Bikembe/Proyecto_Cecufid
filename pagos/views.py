from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from datetime import date
from reportes.utils import registrar_accion
from usuarios.decorators import rol_requerido
from preregistro.models import PreRegistro
from usuarios.models import Nadador, Inscripcion
from asignaciones.models import HorarioCarril, InscripcionCarril
from pagos.models import Pago, Tarifa, Descuento, Producto


@login_required
@rol_requerido(['Administrador', 'Caja'])
def escanear_pago(request):

    registrar_accion(
        usuario=request.user,
        modulo="PAGOS",
        accion="CONSULTA",
        descripcion="Acceso a escaneo de pago",
        request=request
    )

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


def calcular_recargo():
    hoy = date.today()
    dia = hoy.day

    if dia > 5:
        return (dia - 5) * 10
    return 0


def verificar_pago_mes(inscripcion):
    hoy = date.today()

    return Pago.objects.filter(
        inscripcion=inscripcion,
        tipo_pago="MENSUALIDAD",
        mes_pagado__month=hoy.month,
        mes_pagado__year=hoy.year
    ).exists()


def meses_adeudo(inscripcion):
    hoy = date.today()

    pagos = Pago.objects.filter(
        inscripcion=inscripcion,
        tipo_pago="MENSUALIDAD",
        mes_pagado__isnull=False
    ).order_by("-mes_pagado")

    if not pagos.exists():
        return 999

    ultimo_pago = pagos.first().mes_pagado

    diferencia = (hoy.year - ultimo_pago.year) * 12 + (hoy.month - ultimo_pago.month)

    return diferencia


def obtener_siguiente_mes(inscripcion):

    pagos = Pago.objects.filter(
        inscripcion=inscripcion,
        tipo_pago="MENSUALIDAD",
        mes_pagado__isnull=False
    ).order_by("-mes_pagado")

    if not pagos.exists():
        hoy = date.today()
        return date(hoy.year, hoy.month, 1)

    ultimo = pagos.first().mes_pagado

    if ultimo.month == 12:
        return date(ultimo.year + 1, 1, 1)
    else:
        return date(ultimo.year, ultimo.month + 1, 1)


@login_required
@rol_requerido(['Administrador', 'Caja'])
@transaction.atomic
def procesar_pago(request, preregistro_id):

    preregistro = get_object_or_404(PreRegistro, id=preregistro_id)

    dias = [d.strip() for d in preregistro.dias_seleccionados.split(",") if d.strip()]
    total_dias = len(dias)

    tarifa_mensual = Tarifa.objects.filter(
        tipo="MENSUALIDAD",
        dias=total_dias,
        activo=True
    ).first()

    if not tarifa_mensual:
        tarifa_mensual = Tarifa.objects.filter(
            tipo="MENSUALIDAD",
            activo=True
        ).order_by("dias").filter(dias__lte=total_dias).last()

    monto_mensual = tarifa_mensual.monto if tarifa_mensual else 0

    tarifa_inscripcion = Tarifa.objects.filter(tipo="INSCRIPCION", activo=True).first()
    tarifa_examen = Tarifa.objects.filter(tipo="EXAMEN", activo=True).first()

    monto_inscripcion = tarifa_inscripcion.monto if tarifa_inscripcion else 0
    monto_examen = tarifa_examen.monto if tarifa_examen else 0

    recargo = calcular_recargo()

    productos = Producto.objects.filter(activo=True)

    producto_id = request.POST.get("producto")
    cantidad_producto = request.POST.get("cantidad_producto")

    try:
        cantidad_producto = int(cantidad_producto) if cantidad_producto else 0
    except:
        cantidad_producto = 0

    monto_producto = 0
    producto_obj = None

    if producto_id:
        try:
            producto_obj = Producto.objects.get(id=producto_id)
            monto_producto = producto_obj.precio * cantidad_producto
        except:
            pass

    tipo_operacion = request.POST.get("tipo_operacion")

    total = 0

    if tipo_operacion == "INSCRIPCION":
        total = monto_inscripcion
    elif tipo_operacion == "MENSUALIDAD":
        meses = int(request.POST.get("meses", 1))
        total = (monto_mensual * meses) + recargo
    elif tipo_operacion == "EXAMEN":
        total = monto_examen
    elif tipo_operacion == "PRODUCTO":
        total = monto_producto

    if request.method == "POST":

        registrar_accion(
            usuario=request.user,
            modulo="PAGOS",
            accion="PROCESAR",
            descripcion=f"Procesó pago tipo {tipo_operacion} folio {preregistro.folio}",
            request=request
        )

        if tipo_operacion == "INSCRIPCION":
            if preregistro.estado != "APTO":
                messages.error(request, "No apto para inscripción")
                return redirect("pagos:escanear_pago")

        horario = get_object_or_404(HorarioCarril, id=preregistro.plan_id)

        if tipo_operacion == "INSCRIPCION":
            ocupados = InscripcionCarril.objects.filter(
                horario_carril=horario,
                activo=True
            ).count()

            if ocupados >= horario.capacidad_maxima:
                messages.error(request, "Horario lleno")
                return redirect("pagos:escanear_pago")

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

        if nadador.estado != "activo":
            nadador.estado = "activo"
            nadador.save()

        inscripcion, _ = Inscripcion.objects.get_or_create(
            nadador=nadador,
            defaults={"plan_id": preregistro.plan_id}
        )

        if tipo_operacion == "INSCRIPCION":

            registrar_accion(
                usuario=request.user,
                modulo="PAGOS",
                accion="INSCRIPCION",
                descripcion=f"Pago inscripción de {nadador.nombre}",
                request=request
            )

            inscripcion.plan_id = preregistro.plan_id
            inscripcion.save()

            inscripcion_carril, _ = InscripcionCarril.objects.get_or_create(
                nadador=nadador,
                horario_carril=horario,
                defaults={"activo": True}
            )

            inscripcion_carril.activo = True
            inscripcion_carril.save()

            Pago.objects.create(
                preregistro=preregistro,
                inscripcion=inscripcion,
                tipo_pago="INSCRIPCION",
                monto=total,
                metodo_pago=request.POST.get("metodo"),
            )

            preregistro.estado = "INSCRITO"
            preregistro.save()

        elif tipo_operacion == "MENSUALIDAD":

            registrar_accion(
                usuario=request.user,
                modulo="PAGOS",
                accion="MENSUALIDAD",
                descripcion=f"Pago mensualidad de {nadador.nombre}",
                request=request
            )

            meses = int(request.POST.get("meses", 1))
            siguiente = obtener_siguiente_mes(inscripcion)

            lista = []

            for i in range(meses):

                fecha_mes = date(
                    siguiente.year + ((siguiente.month - 1 + i) // 12),
                    ((siguiente.month - 1 + i) % 12) + 1,
                    1
                )

                existe = Pago.objects.filter(
                    inscripcion=inscripcion,
                    tipo_pago="MENSUALIDAD",
                    mes_pagado=fecha_mes
                ).exists()

                if not existe:

                    monto_guardar = monto_mensual + recargo if i == 0 else monto_mensual

                    Pago.objects.create(
                        inscripcion=inscripcion,
                        tipo_pago="MENSUALIDAD",
                        monto=monto_guardar,
                        metodo_pago=request.POST.get("metodo"),
                        mes_pagado=fecha_mes,
                        referencia=f"{fecha_mes.strftime('%B %Y')}"
                    )

                    lista.append(fecha_mes.strftime("%B %Y"))

            if lista:
                messages.success(request, "Pagando: " + ", ".join(lista))

        elif tipo_operacion == "EXAMEN":

            registrar_accion(
                usuario=request.user,
                modulo="PAGOS",
                accion="EXAMEN",
                descripcion=f"Pago examen de {nadador.nombre}",
                request=request
            )

            Pago.objects.create(
                inscripcion=inscripcion,
                tipo_pago="EXAMEN",
                monto=total,
                metodo_pago=request.POST.get("metodo"),
            )

        elif tipo_operacion == "PRODUCTO" and producto_obj and cantidad_producto > 0:

            registrar_accion(
                usuario=request.user,
                modulo="PAGOS",
                accion="PRODUCTO",
                descripcion=f"Venta producto {producto_obj.nombre}",
                request=request
            )

            if producto_obj.stock >= cantidad_producto:

                Pago.objects.create(
                    inscripcion=inscripcion,
                    producto=producto_obj,
                    tipo_pago="PRODUCTO",
                    monto=total,
                    metodo_pago=request.POST.get("metodo"),
                    referencia=f"{producto_obj.nombre} x{cantidad_producto}"
                )

                producto_obj.stock -= cantidad_producto
                producto_obj.save()

            else:
                messages.error(request, "Sin stock")
                return redirect("pagos:procesar_pago", preregistro_id=preregistro.id)

        messages.success(request, "Pago completado")
        return redirect("pagos:procesar_pago", preregistro_id=preregistro.id)

    estado_mensualidad = ""
    try:
        nadador = Nadador.objects.get(codigo_barras=preregistro.folio)
        inscripcion = Inscripcion.objects.get(nadador=nadador)

        deuda = meses_adeudo(inscripcion)

        if deuda < 0:
            deuda = 0

        if deuda == 0:
            estado_mensualidad = "Está al corriente"
        else:
            estado_mensualidad = f"Debe {deuda} mes(es)"

    except:
        pass

    siguiente_mes = None
    try:
        siguiente_mes = obtener_siguiente_mes(inscripcion)
    except:
        pass

    historial = []
    try:
        historial = Pago.objects.filter(
            inscripcion__nadador=nadador
        ).order_by("-id")
    except:
        pass

    return render(request, "pagos/procesar.html", {
        "preregistro": preregistro,
        "total": total,
        "productos": productos,
        "historial": historial,
        "estado_mensualidad": estado_mensualidad,
        "siguiente_mes": siguiente_mes,

        "monto_inscripcion": monto_inscripcion,
        "monto_mensual": monto_mensual,
        "monto_examen": monto_examen,
        "recargo": recargo,
    })


@login_required
@rol_requerido(['Administrador'])
def tarifa_lista(request):

    registrar_accion(
        usuario=request.user,
        modulo="PAGOS",
        accion="CONSULTA",
        descripcion="Listado de tarifas",
        request=request
    )

    tarifas = Tarifa.objects.all()
    return render(request, "pagos/tarifa_lista.html", {"tarifas": tarifas})


@login_required
@rol_requerido(['Administrador'])
def tarifa_crear(request):

    if request.method == "POST":
        tarifa = Tarifa.objects.create(
            nombre=request.POST.get("nombre"),
            tipo=request.POST.get("tipo"),
            dias=request.POST.get("dias") or None,
            monto=request.POST.get("monto"),
            activo=True
        )

        registrar_accion(
            usuario=request.user,
            modulo="PAGOS",
            accion="CREAR",
            descripcion=f"Creó tarifa {tarifa.nombre}",
            request=request
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

        registrar_accion(
            usuario=request.user,
            modulo="PAGOS",
            accion="EDITAR",
            descripcion=f"Editó tarifa {tarifa.nombre}",
            request=request
        )

        return redirect("pagos:tarifa_lista")

    return render(request, "pagos/tarifa_form.html", {"tarifa": tarifa})


@login_required
@rol_requerido(['Administrador'])
def tarifa_eliminar(request, pk):

    tarifa = get_object_or_404(Tarifa, pk=pk)

    registrar_accion(
        usuario=request.user,
        modulo="PAGOS",
        accion="ELIMINAR",
        descripcion=f"Eliminó tarifa {tarifa.nombre}",
        request=request
    )

    tarifa.delete()
    return redirect("pagos:tarifa_lista")


@login_required
@rol_requerido(['Administrador'])
def producto_lista(request):

    registrar_accion(
        usuario=request.user,
        modulo="PAGOS",
        accion="CONSULTA",
        descripcion="Listado de productos",
        request=request
    )

    productos = Producto.objects.all()
    return render(request, "pagos/producto_lista.html", {"productos": productos})


@login_required
@rol_requerido(['Administrador'])
def producto_crear(request):

    if request.method == "POST":
        producto = Producto.objects.create(
            nombre=request.POST.get("nombre"),
            precio=request.POST.get("precio"),
            stock=request.POST.get("stock"),
            activo='activo' in request.POST
        )

        registrar_accion(
            usuario=request.user,
            modulo="PAGOS",
            accion="CREAR",
            descripcion=f"Creó producto {producto.nombre}",
            request=request
        )

        return redirect("pagos:producto_lista")

    return render(request, "pagos/producto_form.html")


@login_required
@rol_requerido(['Administrador'])
def producto_editar(request, pk):

    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":

        producto.nombre = request.POST.get("nombre")
        producto.precio = request.POST.get("precio")
        producto.stock = request.POST.get("stock")
        producto.activo = 'activo' in request.POST
        producto.save()

        registrar_accion(
            usuario=request.user,
            modulo="PAGOS",
            accion="EDITAR",
            descripcion=f"Editó producto {producto.nombre}",
            request=request
        )

        return redirect("pagos:producto_lista")

    return render(request, "pagos/producto_form.html", {"producto": producto})


@login_required
@rol_requerido(['Administrador'])
def producto_eliminar(request, pk):

    producto = get_object_or_404(Producto, pk=pk)

    registrar_accion(
        usuario=request.user,
        modulo="PAGOS",
        accion="ELIMINAR",
        descripcion=f"Eliminó producto {producto.nombre}",
        request=request
    )

    producto.delete()
    return redirect("pagos:producto_lista")


@login_required
@rol_requerido(['Administrador', 'Caja'])
def historial_nadador(request, nadador_id):

    nadador = get_object_or_404(Nadador, id=nadador_id)

    registrar_accion(
        usuario=request.user,
        modulo="PAGOS",
        accion="CONSULTA",
        descripcion=f"Historial de pagos de {nadador.nombre}",
        request=request
    )

    pagos = Pago.objects.filter(
        inscripcion__nadador=nadador
    ).order_by('-mes_pagado', '-fecha_pago')

    return render(request, "pagos/historial_nadador.html", {
        "nadador": nadador,
        "pagos": pagos
    })