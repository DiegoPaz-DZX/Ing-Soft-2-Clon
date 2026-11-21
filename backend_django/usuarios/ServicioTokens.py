import hashlib
from datetime import timedelta

from django.core import signing
from django.utils import timezone

from .TokenInvalidoException import TokenInvalidoException


class ServicioTokens:
    SALT = "kyzen.sesion"
    DURACION_SEGUNDOS = 8 * 60 * 60

    def __init__(self, repositorio, repositorio_revocados=None):
        self._repositorio = repositorio
        self._repositorio_revocados = repositorio_revocados

    def crear(self, cuenta):
        return signing.dumps({"cuenta_id": cuenta.pk}, salt=self.SALT)

    def revocar(self, token):
        if not token:
            raise TokenInvalidoException("La sesión es obligatoria.")
        try:
            datos = signing.loads(token, salt=self.SALT, max_age=self.DURACION_SEGUNDOS)
        except (signing.BadSignature, signing.SignatureExpired) as error:
            raise TokenInvalidoException("La sesión no es válida o ya venció.") from error
        if self._repositorio_revocados is not None:
            self._repositorio_revocados.revocar(
                self._huella(token),
                timezone.now() + timedelta(seconds=self.DURACION_SEGUNDOS),
            )
        return datos

    def obtener_cuenta(self, token):
        if not token:
            raise TokenInvalidoException("La sesión es obligatoria.")
        ahora = timezone.now()
        if self._repositorio_revocados is not None:
            self._repositorio_revocados.eliminar_expirados(ahora)
        if (
            self._repositorio_revocados is not None
            and self._repositorio_revocados.esta_revocado(self._huella(token), ahora)
        ):
            raise TokenInvalidoException("La sesión fue cerrada.")
        try:
            datos = signing.loads(token, salt=self.SALT, max_age=self.DURACION_SEGUNDOS)
        except (signing.BadSignature, signing.SignatureExpired) as error:
            raise TokenInvalidoException("La sesión no es válida o ya venció.") from error
        cuenta = self._repositorio.buscar_por_id(datos.get("cuenta_id"))
        if cuenta is None:
            raise TokenInvalidoException("La cuenta de la sesión ya no existe.")
        return cuenta

    @staticmethod
    def _huella(token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
