from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery
from django.utils import timezone
from datetime import datetime, timedelta

from usuarios.models import Nadador
from .models import Acceso
from usuarios.decorators import rol_requerido
from asignaciones.models import InscripcionCarril

from django.db.models.functions import TruncDate
from django.db.models import Count

from reportes.utils import registrar_accion


@login_required
@rol_requerido(['Administrador', 'Recepcion'])
def escanear_acceso(request):

    mensaje = None
    tipo = None
    estado_actual = None
    info_horario = None
    nadador = None

    hoy = timezone.now().date()
    ahora = timezone.now()

    if request.method == "POST":

        registrar_accion(
            request.user, "ACCESOS", "ESCANEAR",
            "Intento de escaneo de acceso", request
        )

        codigo = request.POST.get("codigo")

        try:
            nadador = Nadador.objects.get(codigo_barras=codigo)

            if nadador.estado.lower().strip() != "activo":
                mensaje = "ACCESO DENEGADO - INACTIVO"
                tipo = "error"

                registrar_accion(
                    request.user, "ACCESOS", "DENEGADO",
                    f"Nadador inactivo: {nadador}", request
                )

            else:

                inscripcion = InscripcionCarril.objects.filter(
                    nadador=nadador,
                    activo=True
                ).select_related('horario_carril').first()

                if not inscripcion:
                    mensaje = "SIN HORARIO ASIGNADO"
                    tipo = "error"

                    registrar_accion(
                        request.user, "ACCESOS", "DENEGADO",
                        f"Sin horario asignado: {nadador}", request
                    )

                else:

                    horario = inscripcion.horario_carril

                    ultimo_acceso = Acceso.objects.filter(
                        nadador=nadador,
                        fecha__date=hoy
                    ).order_by('-fecha').first()

                    # 🔥 PRIMERA VEZ O ENTRADA
                    if not ultimo_acceso or ultimo_acceso.tipo == "SALIDA":

                        hora_inicio = horario.hora_inicio

                        inicio_datetime = timezone.make_aware(
                            datetime.combine(hoy, hora_inicio)
                        )

                        tolerancia = inicio_datetime + timedelta(minutes=5)

                        if ahora > tolerancia:
                            mensaje = "ACCESO BLOQUEADO - FUERA DE TIEMPO"
                            tipo = "error"

                            registrar_accion(
                                request.user, "ACCESOS", "BLOQUEADO",
                                f"Fuera de horario: {nadador}", request
                            )

                        else:
                            nuevo_tipo = "ENTRADA"
                            estado_actual = "DENTRO"

                            Acceso.objects.create(
                                nadador=nadador,
                                tipo=nuevo_tipo
                            )

                            mensaje = "ENTRADA REGISTRADA"
                            tipo = "success"

                            info_horario = horario

                            registrar_accion(
                                request.user, "ACCESOS", "ENTRADA",
                                f"Entrada registrada: {nadador}", request
                            )

                    # 🔥 SALIDA (NO SE VALIDA HORARIO)
                    else:

                        nuevo_tipo = "SALIDA"
                        estado_actual = "FUERA"

                        Acceso.objects.create(
                            nadador=nadador,
                            tipo=nuevo_tipo
                        )

                        mensaje = "SALIDA REGISTRADA"
                        tipo = "success"

                        info_horario = horario

                        registrar_accion(
                            request.user, "ACCESOS", "SALIDA",
                            f"Salida registrada: {nadador}", request
                        )

        except Nadador.DoesNotExist:
            mensaje = "CÓDIGO NO REGISTRADO"
            tipo = "error"

            registrar_accion(
                request.user, "ACCESOS", "ERROR",
                "Código no registrado", request
            )

    subquery = Acceso.objects.filter(
        nadador=OuterRef('pk')
    ).order_by('-fecha')

    nadadores_con_estado = Nadador.objects.annotate(
        ultimo_tipo=Subquery(subquery.values('tipo')[:1])
    )

    dentro_count = nadadores_con_estado.filter(
        ultimo_tipo="ENTRADA"
    ).count()

    return render(request, "escanear.html", {
        "mensaje": mensaje,
        "tipo": tipo,
        "estado_actual": estado_actual,
        "dentro_count": dentro_count,
        "nadador": nadador,
        "info_horario": info_horario
    })


@login_required
@rol_requerido(['Administrador', 'Recepcion'])
def historial_accesos(request):

    registrar_accion(
        request.user, "ACCESOS", "LISTAR",
        "Visualizó historial de accesos", request
    )

    accesos = Acceso.objects.select_related(
        'nadador'
    ).order_by('-fecha')

    return render(request, "accesos/historial_accesos.html", {
        "accesos": accesos
    })