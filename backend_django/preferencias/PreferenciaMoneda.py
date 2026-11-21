from django.db import models

from usuarios.CuentaUsuario import CuentaUsuario

from .Divisa import Divisa


class PreferenciaMoneda(models.Model):
    cuenta = models.OneToOneField(
        CuentaUsuario, on_delete=models.CASCADE, related_name="preferencia_moneda"
    )
    divisa = models.CharField(max_length=3, choices=Divisa.choices, default=Divisa.PEN)
