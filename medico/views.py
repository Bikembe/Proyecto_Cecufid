from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from usuarios.decorators import rol_requerido
from usuarios.models import Nadador
from .models import CertificadoMedico, Medico


@login_required
@rol_requerido(['Medico'])
def escanear_medico(request):

    nadador = None
    mensaje = None

    if request.method == "POST" and "codigo" in request.POST:
        codigo = request.POST.get("codigo")

        try:
            nadador = Nadador.objects.get(codigo_barras=codigo)
        except Nadador.DoesNotExist:
            mensaje = "Código no registrado"

    return render(request, "medico/escanear.html", {
        "nadador": nadador,
        "mensaje": mensaje
    })

@login_required
@rol_requerido(['Medico'])
def crear_certificado(request, nadador_id):

    nadador = get_object_or_404(Nadador, id=nadador_id)
    medico = get_object_or_404(Medico, usuario=request.user)

    if request.method == "POST":

        peso = request.POST.get("peso")
        talla = request.POST.get("talla")

        imc = None
        if peso and talla:
            imc = float(peso) / (float(talla) ** 2)

        CertificadoMedico.objects.create(
            nadador=nadador,
            medico=medico,
            temperatura=request.POST.get("temperatura"),
            presion_arterial=request.POST.get("presion"),
            frecuencia_cardiaca=request.POST.get("fc"),
            frecuencia_respiratoria=request.POST.get("fr"),
            peso=peso,
            talla=talla,
            imc=imc,
            saturacion_oxigeno=request.POST.get("sat"),
            grupo_rh=request.POST.get("rh"),
            alergias=request.POST.get("alergias"),
            afiliacion=request.POST.get("afiliacion"),
            conclusion=request.POST.get("conclusion")
        )

        return redirect("historial_medico", nadador_id=nadador.id)

    return render(request, "medico/formulario.html", {
        "nadador": nadador
    })

@login_required
@rol_requerido(['Medico', 'Administrador'])
def historial_medico(request, nadador_id):

    nadador = get_object_or_404(Nadador, id=nadador_id)

    certificados = CertificadoMedico.objects.filter(
        nadador=nadador
    ).select_related("medico").order_by("-fecha_examen")

    return render(request, "medico/historial.html", {
        "nadador": nadador,
        "certificados": certificados
    })

@login_required
@rol_requerido(['Medico', 'Administrador'])
def imprimir_evaluacion (request, certificado_id):
    
    certificado = get_object_or_404(CertificadoMedico, id=certificado_id)

    return render(request, "medico/imprimir.html", {
        "certificado": certificado
    })