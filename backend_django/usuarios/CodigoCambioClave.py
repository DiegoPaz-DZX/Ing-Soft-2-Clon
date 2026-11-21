from django.db import models

from .CuentaUsuario import CuentaUsuario


class CodigoCambioClave(models.Model):
    cuenta = models.ForeignKey(CuentaUsuario, on_delete=models.CASCADE, related_name="codigos_cambio")
    codigo_hash = models.CharField(max_length=128)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado = models.BooleanField(default=False)
    intentos = models.PositiveSmallIntegerField(default=0)
