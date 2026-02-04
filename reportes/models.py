from django.db import models
from usuarios.models import Usuario

class Reporte(models.Model):
    tipo_reporte = models.CharField(max_length=100)
    descripcion = models.TextField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_generacion = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tipo_reporte

