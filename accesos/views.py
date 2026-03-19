from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery
from usuarios.models import Nadador
from .models import Acceso
from usuarios.decorators import rol_requerido
from asignaciones.models import InscripcionCarril


@login_required
@rol_requerido(['Administrador', 'Caja'])
def escanear_acceso(request):

    mensaje = None
    tipo = None
    estado_actual = None
    info_horario = None
    nadador = None

    if request.method == "POST":
        codigo = request.POST.get("codigo")

        try:
            nadador = Nadador.objects.get(codigo_barras=codigo)

            if nadador.estado.lower().strip() != "activo":
                mensaje = "Acceso Denegado - Nadador Inactivo"
                tipo = "error"

            else:
                ultimo_acceso = Acceso.objects.filter(
                    nadador=nadador
                ).order_by('-fecha').first()

                if not ultimo_acceso:
                    nuevo_tipo = "ENTRADA"
                    estado_actual = "DENTRO"

                elif ultimo_acceso.tipo == "ENTRADA":
                    nuevo_tipo = "SALIDA"
                    estado_actual = "FUERA"

                else:
                    nuevo_tipo = "ENTRADA"
                    estado_actual = "DENTRO"

                Acceso.objects.create(
                    nadador=nadador,
                    tipo=nuevo_tipo
                )

                mensaje = f"{nuevo_tipo} registrada"
                tipo = "success"

                inscripcion = InscripcionCarril.objects.filter(
                    nadador=nadador,
                    activo=True
                ).select_related(
                    'horario_carril__carril',
                    'horario_carril__maestro',
                    'horario_carril__nivel'
                ).first()

                if inscripcion:
                    info_horario = inscripcion.horario_carril

        except Nadador.DoesNotExist:
            mensaje = "Código no registrado"
            tipo = "error"

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