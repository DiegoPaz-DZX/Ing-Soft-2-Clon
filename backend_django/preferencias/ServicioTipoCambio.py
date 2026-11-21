from decimal import Decimal

from django.utils import timezone

from .TipoCambio import TipoCambio
from .TipoCambioNoDisponibleException import TipoCambioNoDisponibleException


class ServicioTipoCambio:
    def __init__(self, proveedor, repositorio, valor_de_respaldo):
        self._proveedor = proveedor
        self._repositorio = repositorio
        self._valor_de_respaldo = Decimal(str(valor_de_respaldo))

    def obtener_del_dia(self, hoy=None):
        hoy = hoy or timezone.localdate()
        guardado = self._repositorio.obtener_de_fecha(hoy)
        if guardado is not None:
            return guardado
        try:
            valor = self._proveedor.obtener_soles_por_dolar()
        except TipoCambioNoDisponibleException:
            return self._usar_respaldo(hoy)
        return self._repositorio.guardar(hoy, valor, self._proveedor.nombre)

    def _usar_respaldo(self, hoy):
        ultimo = self._repositorio.obtener_ultimo()
        if ultimo is not None:
            return ultimo
        return TipoCambio(hoy, self._valor_de_respaldo, "Valor referencial")
