import json
from decimal import Decimal, InvalidOperation
from urllib.error import URLError
from urllib.request import urlopen

from .ProveedorTipoCambio import ProveedorTipoCambio
from .TipoCambioNoDisponibleException import TipoCambioNoDisponibleException


class ProveedorTipoCambioApi(ProveedorTipoCambio):
    nombre = "open.er-api.com"

    def __init__(self, url, segundos_de_espera=4):
        self._url = url
        self._segundos_de_espera = segundos_de_espera

    def obtener_soles_por_dolar(self):
        try:
            with urlopen(self._url, timeout=self._segundos_de_espera) as respuesta:
                datos = json.loads(respuesta.read().decode("utf-8"))
            valor = Decimal(str(datos["rates"]["PEN"]))
        except (URLError, TimeoutError, ValueError, KeyError, TypeError, InvalidOperation) as error:
            raise TipoCambioNoDisponibleException("No se pudo consultar el tipo de cambio.") from error
        if valor <= 0:
            raise TipoCambioNoDisponibleException("El tipo de cambio recibido no es válido.")
        return valor.quantize(Decimal("0.0001"))
