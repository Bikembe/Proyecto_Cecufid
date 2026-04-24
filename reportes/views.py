from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from usuarios.models import Usuario
from .models import HistorialAccion, UsuarioActivo, Reporte
from usuarios.decorators import rol_requerido
from django.db.models import Sum
from datetime import datetime, timedelta
from pagos.models import Pago
from openpyxl import Workbook
from django.http import HttpResponse
from django.db.models.functions import TruncDate
from django.db.models.functions import TruncMonth
from django.utils import timezone
from usuarios.models import Sede
from django.core.paginator import Paginator

@rol_requerido(['Administrador', 'Coordinador'])
def reporte_por_sede(request):

    sede_id = request.GET.get("sede")
    fecha_inicio = request.GET.get("inicio")
    fecha_fin = request.GET.get("fin")

    sedes = Sede.objects.all()
    pagos = Pago.objects.select_related("inscripcion__plan__sede")

    if sede_id:
        pagos = pagos.filter(inscripcion__plan__sede_id=sede_id)

    if fecha_inicio:
        pagos = pagos.filter(fecha_pago__gte=fecha_inicio)

    if fecha_fin:
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)
        pagos = pagos.filter(fecha_pago__lt=fecha_fin_dt)

    if not fecha_inicio and not fecha_fin:
        hoy = timezone.now().date()
        manana = hoy + timedelta(days=1)
        pagos = pagos.filter(fecha_pago__gte=hoy, fecha_pago__lt=manana)

    total_general = pagos.aggregate(total=Sum("monto"))['total'] or 0

    total_inscripciones = pagos.filter(tipo_pago="INSCRIPCION").aggregate(total=Sum("monto"))['total'] or 0
    total_mensualidades = pagos.filter(tipo_pago="MENSUALIDAD").aggregate(total=Sum("monto"))['total'] or 0
    total_examenes = pagos.filter(tipo_pago="EXAMEN").aggregate(total=Sum("monto"))['total'] or 0
    total_productos = pagos.filter(tipo_pago="PRODUCTO").aggregate(total=Sum("monto"))['total'] or 0

    pagos = pagos.order_by("-id")

    return render(request, "reportes/reporte_sede.html", {
        "sedes": sedes,
        "pagos": pagos,
        "sede_id": sede_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,

        "total_general": total_general,
        "total_inscripciones": total_inscripciones,
        "total_mensualidades": total_mensualidades,
        "total_examenes": total_examenes,
        "total_productos": total_productos,
    })

@rol_requerido(['Administrador', 'Coordinador'])
def reporte_mensual(request):

    datos = (
        Pago.objects
        .annotate(mes=TruncMonth("fecha_pago"))
        .values("mes")
        .annotate(total=Sum("monto"))
        .order_by("mes")
    )

    return render(request, "reportes/reporte_mensual.html", {
        "datos": datos
    })

from usuarios.models import Usuario
from django.db.models import Sum

@rol_requerido(['Administrador', 'Coordinador'])
def corte_caja(request):

    usuarios = Usuario.objects.all()

    usuario_id = request.GET.get("usuario")
    pagos = Pago.objects.all()

    if usuario_id:
        pagos = pagos.filter(usuario_id=usuario_id)

    total = pagos.aggregate(total=Sum("monto"))['total'] or 0

    return render(request, "reportes/corte_caja.html", {
        "usuarios": usuarios,
        "pagos": pagos.order_by("-id"),
        "total": total,
        "usuario_id": usuario_id
    })

@rol_requerido(['Administrador', 'Coordinador'])
def grafica_ingresos(request):

    datos = (
        Pago.objects
        .annotate(dia=TruncDate("fecha_pago"))
        .values("dia")
        .annotate(total=Sum("monto"))
        .order_by("dia")
    )

    fechas = [str(d["dia"]) for d in datos]
    totales = [float(d["total"]) for d in datos]

    return render(request, "reportes/grafica.html", {
        "fechas": fechas,
        "totales": totales
    })

@rol_requerido(['Administrador', 'Coordinador'])
def exportar_excel_caja(request):

    pagos = Pago.objects.all().order_by("-id")

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Caja"
    ws.append(["Fecha", "Tipo", "Detalle", "Monto", "Método"])

    for p in pagos:
        detalle = ""

        if p.tipo_pago == "MENSUALIDAD" and p.mes_pagado:
            detalle = p.mes_pagado.strftime("%B %Y")
        else:
            detalle = p.referencia or ""

        ws.append([
            str(p.fecha_pago),
            p.tipo_pago,
            detalle,
            float(p.monto),
            p.metodo_pago
        ])

    response = HttpResponse(
        content_type="application/ms-excel"
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_caja.xlsx"'

    wb.save(response)
    return response

@rol_requerido(['Administrador', 'Coordinador'])
def reporte_caja(request):

    fecha_inicio = request.GET.get("inicio")
    fecha_fin = request.GET.get("fin")
    tipo = request.GET.get("tipo") 

    pagos = Pago.objects.all()

    if fecha_inicio:
        pagos = pagos.filter(fecha_pago__gte=fecha_inicio)

    if fecha_fin:
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)
        pagos = pagos.filter(fecha_pago__lt=fecha_fin_dt)

    if not fecha_inicio and not fecha_fin:
        hoy = timezone.now().date()
        manana = hoy + timedelta(days=1)
        pagos = pagos.filter(fecha_pago__gte=hoy, fecha_pago__lt=manana)

    if tipo:
        pagos = pagos.filter(tipo_pago=tipo)

    total_general = pagos.aggregate(total=Sum('monto'))['total'] or 0

    total_inscripciones = pagos.filter(tipo_pago="INSCRIPCION").aggregate(total=Sum('monto'))['total'] or 0
    total_mensualidades = pagos.filter(tipo_pago="MENSUALIDAD").aggregate(total=Sum('monto'))['total'] or 0
    total_examenes = pagos.filter(tipo_pago="EXAMEN").aggregate(total=Sum('monto'))['total'] or 0
    total_productos = pagos.filter(tipo_pago="PRODUCTO").aggregate(total=Sum('monto'))['total'] or 0

    pagos = pagos.order_by("-id")

    return render(request, "reportes/reporte_caja.html", {
        "pagos": pagos,
        "total_general": total_general,
        "total_inscripciones": total_inscripciones,
        "total_mensualidades": total_mensualidades,
        "total_examenes": total_examenes,
        "total_productos": total_productos,

        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "tipo": tipo,
    })

@rol_requerido(['Administrador', 'Coordinador'])
def historial_lista(request):

    historial = HistorialAccion.objects.select_related('usuario').all().order_by('-fecha')

    usuario = request.GET.get('usuario', '').strip()
    modulo = request.GET.get('modulo', '').strip()
    accion = request.GET.get('accion', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()

    usuarios = (
        HistorialAccion.objects
        .values_list('usuario__email', flat=True)
        .order_by('usuario__email')
        .distinct()
    )

    modulos = (
        HistorialAccion.objects
        .values_list('modulo', flat=True)
        .order_by('modulo')
        .distinct()
    )

    acciones = (
        HistorialAccion.objects
        .values_list('accion', flat=True)
        .order_by('accion')
        .distinct()
    )

    usuarios = [u for u in usuarios if u]
    modulos = [m for m in modulos if m]
    acciones = [a for a in acciones if a]

    if usuario:
        historial = historial.filter(usuario__email=usuario)

    if modulo:
        historial = historial.filter(modulo=modulo)

    if accion:
        historial = historial.filter(accion=accion)

    if fecha_inicio:
        try:
            historial = historial.filter(fecha__date__gte=fecha_inicio)
        except:
            pass

    if fecha_fin:
        try:
            historial = historial.filter(fecha__date__lte=fecha_fin)
        except:
            pass

    paginator = Paginator(historial, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'reportes/historial.html', {
        'historial': page_obj,
        'page_obj': page_obj,
        'usuarios': usuarios,
        'modulos': modulos,
        'acciones': acciones,
    })

@rol_requerido(['Administrador', 'Coordinador'])
def usuarios_en_linea(request):
    limite = timezone.now() - timedelta(minutes=5)

    usuarios = UsuarioActivo.objects.select_related('usuario').filter(
        ultima_actividad__gte=limite
    )

    return render(request, 'reportes/usuarios_online.html', {
        'usuarios': usuarios
    })


@rol_requerido(['Administrador', 'Coordinador'])
def reporte_lista(request):
    reportes = Reporte.objects.select_related('generado_por').all()

    return render(request, 'reportes/reporte_lista.html', {
        'reportes': reportes
    })