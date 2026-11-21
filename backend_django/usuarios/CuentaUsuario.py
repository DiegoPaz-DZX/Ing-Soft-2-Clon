from django.contrib.auth.hashers import check_password, make_password
from django.db import models

from .RolUsuario import RolUsuario


class CuentaUsuario(models.Model):
    correo = models.EmailField(unique=True)
    clave_hash = models.CharField(max_length=128)
    rol = models.CharField(max_length=15, choices=RolUsuario.choices, default=RolUsuario.USUARIO)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def definir_clave(self, clave):
        self.clave_hash = make_password(clave)

    def verificar_clave(self, clave):
        return check_password(clave, self.clave_hash)
