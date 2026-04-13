from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Medico


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_medico_si_es_rol(sender, instance, created, **kwargs):

    if created:
        if hasattr(instance, "rol") and instance.rol and instance.rol.nombre == "Medico":
            Medico.objects.create(
                usuario=instance,
                nombre_completo=f"{instance.first_name} {instance.last_name}",
                cedula_profesional="SIN REGISTRAR"
            )