from usuarios.CuentaUsuario import CuentaUsuario

from .PreferenciaMoneda import PreferenciaMoneda
from .RepositorioPreferencias import RepositorioPreferencias


class RepositorioPreferenciasDjango(RepositorioPreferencias):
    def existe_cuenta(self, cuenta_id):
        return CuentaUsuario.objects.filter(pk=cuenta_id).exists()

    def obtener_divisa(self, cuenta_id):
        preferencia = PreferenciaMoneda.objects.filter(cuenta_id=cuenta_id).first()
        return preferencia.divisa if preferencia else None

    def guardar_divisa(self, cuenta_id, divisa):
        PreferenciaMoneda.objects.update_or_create(cuenta_id=cuenta_id, defaults={"divisa": divisa})
