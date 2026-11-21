import re

from .CredencialesInvalidasException import CredencialesInvalidasException


class ProveedorAutenticacion:
    FORMATO_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    def __init__(self, estrategia):
        self._estrategia = estrategia

    def cambiar_estrategia(self, estrategia):
        self._estrategia = estrategia

    def iniciar_sesion(self, correo, clave):
        self._validar(correo, clave)
        cuenta = self._estrategia.autenticar(correo.strip().lower(), clave)
        if cuenta is None:
            raise CredencialesInvalidasException("Correo o contraseña incorrectos.")
        return cuenta

    def _validar(self, correo, clave):
        if not isinstance(correo, str) or not correo.strip() or not isinstance(clave, str) or not clave:
            raise CredencialesInvalidasException("Debe ingresar su correo y contraseña.")
        if not self.FORMATO_CORREO.match(correo.strip()):
            raise CredencialesInvalidasException("El formato del correo no es válido.")
