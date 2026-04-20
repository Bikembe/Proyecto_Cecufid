from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from usuarios.decorators import rol_requerido
from usuarios.models import Nadador, Usuario
from preregistro.models import PreRegistro
from .models import CertificadoMedico, Medico
from reportes.utils import registrar_accion


@login_required
@rol_requerido(['Medico', 'Administrador'])
def escanear_medico(request):

    nadador = None
    preregistro = None
    mensaje = None

    if request.method == "POST":
        codigo = request.POST.get("codigo")

        try:
            nadador = Nadador.objects.get(codigo_barras=codigo)

            registrar_accion(
                usuario=request.user,
                modulo="MEDICO",
                accion="CONSULTA",
                descripcion=f"Escaneo exitoso de nadador {codigo}",
                request=request
            )

        except Nadador.DoesNotExist:
            try:
                preregistro = PreRegistro.objects.get(folio=codigo)

                registrar_accion(
                    usuario=request.user,
                    modulo="MEDICO",
                    accion="CONSULTA",
                    descripcion=f"Escaneo de preregistro {codigo}",
                    request=request
                )

            except PreRegistro.DoesNotExist:
                mensaje = "Código no registrado"

                registrar_accion(
                    usuario=request.user,
                    modulo="MEDICO",
                    accion="CONSULTA",
                    descripcion=f"Escaneo fallido {codigo}",
                    request=request
                )

    return render(request, "medico/escanear.html", {
        "nadador": nadador,
        "preregistro": preregistro,
        "mensaje": mensaje
    })


@login_required
@rol_requerido(['Medico', 'Administrador'])
def crear_certificado(request, nadador_id):

    nadador = get_object_or_404(Nadador, id=nadador_id)
    medico = Medico.objects.filter(usuario=request.user).first()

    if not medico:
        return render(request, "medico/formulario.html", {
            "error": "Este usuario no tiene perfil médico asignado"
        })

    if request.method == "POST":

        peso = request.POST.get("peso")
        talla = request.POST.get("talla")

        imc = None
        if peso and talla:
            try:
                imc = float(peso) / (float(talla) ** 2)
            except:
                imc = None

        certificado = CertificadoMedico.objects.create(
            nadador=nadador,
            medico=medico,
            temperatura=request.POST.get("temperatura") or None,
            presion_arterial=request.POST.get("presion") or "",
            frecuencia_cardiaca=request.POST.get("fc") or None,
            frecuencia_respiratoria=request.POST.get("fr") or None,
            peso=peso or None,
            talla=talla or None,
            imc=imc,
            saturacion_oxigeno=request.POST.get("sat") or None,
            grupo_rh=request.POST.get("rh") or "",
            alergias=request.POST.get("alergias") or "",
            afiliacion=request.POST.get("afiliacion") or "",
            motivos=request.POST.get("motivos") or "",
            conclusion=request.POST.get("conclusion"),
            estatus=request.POST.get("estatus"),
        )

        preregistro = PreRegistro.objects.filter(
            nombre=nadador.nombre,
            apellido_paterno=nadador.apellido_paterno
        ).order_by("-id").first()

        if preregistro:
            preregistro.estado = "APTO" if certificado.estatus == "APTO" else "NO_APTO"
            preregistro.save()

        registrar_accion(
            usuario=request.user,
            modulo="MEDICO",
            accion="CREAR",
            descripcion=f"Certificado médico creado para nadador {nadador.id}",
            request=request
        )

        return redirect("medico:historial_medico", nadador_id=nadador.id)


@login_required
@rol_requerido(['Medico', 'Administrador'])
def crear_certificado_preregistro(request, preregistro_id):

    preregistro = get_object_or_404(PreRegistro, id=preregistro_id)
    medico = Medico.objects.filter(usuario=request.user).first()

    if not medico:
        return render(request, "medico/formulario.html", {
            "error": "Este usuario no tiene perfil médico asignado"
        })

    if request.method == "POST":

        peso = request.POST.get("peso")
        talla = request.POST.get("talla")

        imc = None
        if peso and talla:
            try:
                imc = float(peso) / (float(talla) ** 2)
            except:
                imc = None

        certificado = CertificadoMedico.objects.create(
            preregistro=preregistro,
            medico=medico,
            temperatura=request.POST.get("temperatura") or None,
            presion_arterial=request.POST.get("presion") or "",
            frecuencia_cardiaca=request.POST.get("fc") or None,
            frecuencia_respiratoria=request.POST.get("fr") or None,
            peso=peso or None,
            talla=talla or None,
            imc=imc,
            saturacion_oxigeno=request.POST.get("sat") or None,
            grupo_rh=request.POST.get("rh") or "",
            alergias=request.POST.get("alergias") or "",
            afiliacion=request.POST.get("afiliacion") or "",
            motivos=request.POST.get("motivos") or "",
            conclusion=request.POST.get("conclusion"),
            estatus=request.POST.get("estatus"),
        )

        preregistro.estado = "APTO" if certificado.estatus == "APTO" else "NO_APTO"
        preregistro.save()

        registrar_accion(
            usuario=request.user,
            modulo="MEDICO",
            accion="CREAR",
            descripcion=f"Certificado creado desde preregistro {preregistro.id}",
            request=request
        )

        return redirect("medico:historial_medico_preregistro", preregistro_id=preregistro.id)


@login_required
@rol_requerido(['Medico', 'Administrador'])
def historial_medico(request, nadador_id):

    nadador = get_object_or_404(Nadador, id=nadador_id)

    certificados = CertificadoMedico.objects.filter(
        nadador=nadador
    ).select_related("medico").order_by("-fecha_examen")

    registrar_accion(
        usuario=request.user,
        modulo="MEDICO",
        accion="CONSULTA",
        descripcion=f"Consulta historial médico nadador {nadador_id}",
        request=request
    )

    return render(request, "medico/historial.html", {
        "nadador": nadador,
        "certificados": certificados
    })


@login_required
@rol_requerido(['Medico', 'Administrador'])
def historial_medico_preregistro(request, preregistro_id):

    preregistro = get_object_or_404(PreRegistro, id=preregistro_id)

    certificados = CertificadoMedico.objects.filter(
        preregistro=preregistro
    ).select_related("medico").order_by("-fecha_examen")

    registrar_accion(
        usuario=request.user,
        modulo="MEDICO",
        accion="CONSULTA",
        descripcion=f"Consulta historial preregistro {preregistro_id}",
        request=request
    )

    return render(request, "medico/historial.html", {
        "preregistro": preregistro,
        "certificados": certificados
    })


@login_required
@rol_requerido(['Medico', 'Administrador'])
def imprimir_evaluacion(request, certificado_id):

    certificado = get_object_or_404(CertificadoMedico, id=certificado_id)

    registrar_accion(
        usuario=request.user,
        modulo="MEDICO",
        accion="CONSULTA",
        descripcion=f"Impresión certificado {certificado_id}",
        request=request
    )

    return render(request, "medico/imprimir.html", {
        "certificado": certificado
    })


@login_required
@rol_requerido(['Medico', 'Administrador'])
def historial_general(request):

    certificados = CertificadoMedico.objects.select_related(
        "medico",
        "nadador",
        "preregistro"
    ).order_by("-fecha_examen")

    medicos = Medico.objects.all()

    medico_id = request.GET.get("medico")
    fecha = request.GET.get("fecha")
    estatus = request.GET.get("estatus")

    if medico_id:
        certificados = certificados.filter(medico_id=medico_id)

    if fecha:
        certificados = certificados.filter(fecha_examen__date=fecha)

    if estatus:
        certificados = certificados.filter(estatus=estatus)

    registrar_accion(
        usuario=request.user,
        modulo="MEDICO",
        accion="CONSULTA",
        descripcion="Consulta historial general",
        request=request
    )

    return render(request, "medico/historial_general.html", {
        "certificados": certificados,
        "medicos": medicos,
        "filtros": {
            "medico": medico_id,
            "fecha": fecha,
            "estatus": estatus
        }
    })


@login_required
@rol_requerido(['Administrador'])
def medico_lista(request):

    medicos = Medico.objects.select_related("usuario")

    registrar_accion(
        usuario=request.user,
        modulo="MEDICO",
        accion="CONSULTA",
        descripcion="Listado de médicos",
        request=request
    )

    return render(request, "medico/medico_lista.html", {
        "medicos": medicos
    })


@login_required
@rol_requerido(['Administrador'])
def medico_crear(request):

    usuarios = Usuario.objects.filter(rol__nombre="Medico")

    if request.method == "POST":
        usuario_id = request.POST.get("usuario")
        nombre = request.POST.get("nombre_completo")
        cedula = request.POST.get("cedula")

        try:
            Medico.objects.create(
                usuario_id=usuario_id,
                nombre_completo=nombre,
                cedula_profesional=cedula
            )

            registrar_accion(
                usuario=request.user,
                modulo="MEDICO",
                accion="CREAR",
                descripcion=f"Nuevo médico creado {nombre}",
                request=request
            )

            return redirect("medico:medico_lista")

        except Exception as e:
            return render(request, "medico/medico_form.html", {
                "usuarios": usuarios,
                "error": str(e)
            })

    return render(request, "medico/medico_form.html", {
        "usuarios": usuarios
    })


@login_required
@rol_requerido(['Administrador'])
def medico_editar(request, pk):

    medico = get_object_or_404(Medico, pk=pk)
    usuarios = Usuario.objects.filter(rol__nombre="Medico")

    if request.method == "POST":

        medico.usuario_id = request.POST.get("usuario")
        medico.nombre_completo = request.POST.get("nombre_completo")
        medico.cedula_profesional = request.POST.get("cedula")

        medico.save()

        registrar_accion(
            usuario=request.user,
            modulo="MEDICO",
            accion="EDITAR",
            descripcion=f"Médico editado {medico.id}",
            request=request
        )

        return redirect("medico:medico_lista")

    return render(request, "medico/medico_form.html", {
        "medico": medico,
        "usuarios": usuarios
    })


@login_required
@rol_requerido(['Administrador'])
def medico_eliminar(request, pk):

    medico = get_object_or_404(Medico, pk=pk)
    medico.delete()

    registrar_accion(
        usuario=request.user,
        modulo="MEDICO",
        accion="ELIMINAR",
        descripcion=f"Médico eliminado {pk}",
        request=request
    )

    return redirect("medico:medico_lista")