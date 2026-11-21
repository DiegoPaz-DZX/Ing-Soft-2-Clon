from cryptography.fernet import InvalidToken
from django.db import models

from .FabricaCifradores import FabricaCifradores


class CampoTextoCifrado(models.TextField):
    PREFIJO = "kyzen:cifrado:"
    def get_db_prep_save(self, valor, connection):
        if valor in (None, "") or hasattr(valor, "as_sql"):
            return valor
        return super().get_db_prep_save(valor, connection)

    def from_db_value(self, valor, expresion, conexion):
        return self._descifrar_si_corresponde(valor, conexion)

    def to_python(self, valor):
        return self._descifrar_si_corresponde(valor)

    def get_prep_value(self, valor):
        valor = super().get_prep_value(valor)
        if valor in (None, "") or self._esta_cifrado(valor):
            return valor
        cifrador = FabricaCifradores.crear_cifrador_datos()
        return self.PREFIJO + cifrador.cifrar(valor)

    def _descifrar_si_corresponde(self, valor, conexion=None):
        if valor in (None, "") or not isinstance(valor, str):
            return valor
        if not valor.startswith(self.PREFIJO):
            return valor
        token = valor[len(self.PREFIJO):]
        try:
            return FabricaCifradores.crear_cifrador_datos().descifrar(token)
        except InvalidToken as error:
            raise ValueError("No se pudo descifrar la información del movimiento.") from error

    def _esta_cifrado(self, valor):
        if not isinstance(valor, str) or not valor.startswith(self.PREFIJO):
            return False
        try:
            FabricaCifradores.crear_cifrador_datos().descifrar(valor[len(self.PREFIJO):])
            return True
        except InvalidToken:
            return False
