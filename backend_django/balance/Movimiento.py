import mimetypes
import os

from django.db import models

from seguridad.CampoTextoCifrado import CampoTextoCifrado
from usuarios.CuentaUsuario import CuentaUsuario
from metas.models import MetaAhorro

from .MontoInvalidoException import MontoInvalidoException
from .TipoMovimiento import TipoMovimiento


class Movimiento(models.Model):
    tipo = models.CharField(max_length=7, choices=TipoMovimiento.choices)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    descripcion = CampoTextoCifrado(max_length=200)
    categoria = models.CharField(max_length=30, blank=True, default="")
    comprobante = models.FileField(upload_to="comprobantes/", null=True, blank=True)
    moneda = models.CharField(
        max_length=3,
        choices=[("PEN", "Soles"), ("USD", "Dólares")],
        default="PEN",
    )
    usuario = models.ForeignKey(
        CuentaUsuario,
        on_delete = models.CASCADE,
        related_name = 'movimientos',
        null = True,
        blank = True,
    )
    meta = models.ForeignKey(
        MetaAhorro,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_ahorro",
    )

    def save(self, *args, **kwargs):
        if self.monto <= 0:
            raise MontoInvalidoException("El monto debe ser mayor que cero")
        super().save(*args, **kwargs)

    def datos_comprobante(self):
        if not self.comprobante:
            return None
        tipo, _ = mimetypes.guess_type(self.comprobante.name)
        return {
            "nombre": os.path.basename(self.comprobante.name),
            "tipo": tipo or "application/octet-stream",
            "url": self.comprobante.url,
        }
