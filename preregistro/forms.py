from django import forms
from .models import PreRegistro


class PreRegistroForm(forms.ModelForm):

    class Meta:
        model = PreRegistro
        fields = [
            "nombre",
            "apellido_paterno",
            "apellido_materno",
            "fecha_nacimiento",
            "sexo",
            "telefono",
            "correo",
            "foto",
            "acta_nacimiento",
            "curp",
            "identificacion",
            "categoria",
            "plan",
            "dias_seleccionados",
            "acepta_terminos",
            "firma_digital",
        ]

        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
            "dias_seleccionados": forms.TextInput(attrs={"placeholder": "LUN-MIE-VIE"}),
        }