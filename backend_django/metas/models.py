from django.db import models
from django.db.models.functions import Lower

from usuarios.CuentaUsuario import CuentaUsuario


class MetaAhorro(models.Model):
    usuario = models.ForeignKey(CuentaUsuario, on_delete=models.CASCADE, related_name="metas")
    nombre = models.CharField(max_length=120)
    objetivo_pen = models.DecimalField(max_digits=12, decimal_places=2)
    total_abonado_pen = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-actualizada_en", "-id"]
        constraints = [
            models.UniqueConstraint(
                Lower("nombre"),
                "usuario",
                name="meta_nombre_unico_por_usuario",
            ),
        ]
