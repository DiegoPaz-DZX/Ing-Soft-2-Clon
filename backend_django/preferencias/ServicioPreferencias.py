from .CuentaNoEncontradaException import CuentaNoEncontradaException
from .Divisa import Divisa
from .FabricaConversores import FabricaConversores
from .PreferenciaActual import PreferenciaActual


class ServicioPreferencias:
    def __init__(self, repositorio, servicio_tipo_cambio):
        self._repositorio = repositorio
        self._tipo_cambio = servicio_tipo_cambio

    def obtener_preferencia(self, cuenta_id):
        self._validar_cuenta(cuenta_id)
        codigo = self._repositorio.obtener_divisa(cuenta_id) or Divisa.PEN
        return self._armar_preferencia(codigo)

    def cambiar_divisa(self, cuenta_id, codigo):
        self._validar_cuenta(cuenta_id)
        preferencia = self._armar_preferencia(str(codigo or "").upper())
        self._repositorio.guardar_divisa(cuenta_id, preferencia.divisa.codigo)
        return preferencia

    def _armar_preferencia(self, codigo):
        tipo_cambio = self._tipo_cambio.obtener_del_dia()
        return PreferenciaActual(
            divisa=FabricaConversores.crear(codigo, tipo_cambio.soles_por_dolar),
            opciones=FabricaConversores.crear_todos(tipo_cambio.soles_por_dolar),
            tipo_cambio=tipo_cambio,
        )

    def _validar_cuenta(self, cuenta_id):
        if not self._repositorio.existe_cuenta(cuenta_id):
            raise CuentaNoEncontradaException("La cuenta no existe.")
