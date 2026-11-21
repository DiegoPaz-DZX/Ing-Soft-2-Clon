import re

from .CorreoRegistradoException import CorreoRegistradoException
from .CuentaUsuario import CuentaUsuario
from .DatosRegistroInvalidosException import DatosRegistroInvalidosException


class ServicioRegistro:
    FORMATO_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    def __init__(self, repositorio):
        self._repositorio = repositorio

    def registrar(self, correo, clave, confirmacion):
        self._validar(correo, clave, confirmacion)
        correo_limpio = correo.strip().lower()

        if self._repositorio.buscar_por_correo(correo_limpio) is not None:
            raise CorreoRegistradoException("Este correo ya está registrado.")

        cuenta = CuentaUsuario(correo=correo_limpio)
        cuenta.definir_clave(clave)
        self._repositorio.guardar(cuenta)
        return cuenta

    def _validar(self, correo, clave, confirmacion):
        if not isinstance(correo, str) or not self.FORMATO_CORREO.match(correo.strip()):
            raise DatosRegistroInvalidosException("Ingresa un correo válido.")
        if (
            not isinstance(clave, str)
            or len(clave) < 8
            or re.search(r"[A-Za-z]", clave) is None
            or re.search(r"[0-9]", clave) is None
        ):
            raise DatosRegistroInvalidosException(
                "La contraseña debe tener 8 caracteres, una letra y un número."
            )
        if clave != confirmacion:
            raise DatosRegistroInvalidosException("Las contraseñas no coinciden.")
