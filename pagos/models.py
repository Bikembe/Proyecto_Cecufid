from django.db import models
from usuarios.models import Inscripcion

class Pago(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)
    fecha_pago = models.DateField()
    estado = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.id} - {self.monto}"
