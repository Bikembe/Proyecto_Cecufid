from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from usuarios.models import Usuario
from .models import HistorialAccion, UsuarioActivo, Reporte

def historial_lista(request):
    historial = HistorialAccion.objects.select_related('usuario').all()

    return render(request, 'reportes/historial.html', {
        'historial': historial
    })

def usuarios_en_linea(request):
    limite = timezone.now() - timedelta(minutes=5)

    usuarios = UsuarioActivo.objects.select_related('usuario').filter(
        ultima_actividad__gte=limite
    )

    return render(request, 'reportes/usuarios_online.html', {
        'usuarios': usuarios
    })

def reporte_lista(request):
    reportes = Reporte.objects.select_related('generado_por').all()

    return render(request, 'reportes/reporte_lista.html', {
        'reportes': reportes
    })