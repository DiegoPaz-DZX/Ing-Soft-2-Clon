import base64
import hashlib
import os

from django.conf import settings

from .CifradorFernet import CifradorFernet


class FabricaCifradores:
    @staticmethod
    def crear_cifrador_datos():
        clave_configurada = os.environ.get("KYZEN_DATA_KEY")
        if clave_configurada:
            clave = clave_configurada.encode("utf-8")
        else:
            resumen = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
            clave = base64.urlsafe_b64encode(resumen)
        return CifradorFernet(clave)
