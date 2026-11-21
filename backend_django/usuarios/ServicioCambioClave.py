import secrets
import string
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone


class ServicioCambioClave:
    def __init__(self, repositorio, repositorio_codigos, servicio_correo):
        self._repositorio = repositorio
        self._repositorio_codigos = repositorio_codigos
        self._servicio_correo = servicio_correo

    def generar_codigo(self, correo):
        correo_limpio = correo.strip().lower()
        cuenta = self._repositorio.buscar_por_correo(correo_limpio)
        if cuenta is None:
            raise ValueError("No existe una cuenta con ese correo.")

        codigo = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        with transaction.atomic():
            self._repositorio_codigos.invalidar_activos(cuenta)
            self._repositorio_codigos.crear(
                cuenta,
                make_password(codigo),
                timezone.now() + timedelta(minutes=10),
            )
            self._servicio_correo.enviar_codigo_cambio(correo_limpio, codigo)
        return True

    def cambiar_clave(self, correo, codigo, nueva_clave, confirmacion_clave):
        correo_limpio = correo.strip().lower()
        cuenta = self._repositorio.buscar_por_correo(correo_limpio)

        if cuenta is None:
            raise ValueError("No existe una cuenta con ese correo.")
        with transaction.atomic():
            solicitud = self._repositorio_codigos.obtener_pendiente(cuenta)
            if solicitud is None or solicitud.expira_en <= timezone.now():
                raise ValueError("El código expiró. Solicita uno nuevo.")
            if solicitud.intentos >= 5:
                raise ValueError("Se superó el límite de intentos. Solicita un código nuevo.")
            solicitud.intentos += 1
            self._repositorio_codigos.guardar_intentos(solicitud)

        if not check_password(codigo.strip().upper(), solicitud.codigo_hash):
            raise ValueError("El código no es correcto.")
        if len(nueva_clave) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if nueva_clave != confirmacion_clave:
            raise ValueError("Las contraseñas no coinciden.")

        cuenta.clave_hash = make_password(nueva_clave)
        cuenta.save(update_fields=["clave_hash"])
        self._repositorio_codigos.marcar_usado(solicitud)
