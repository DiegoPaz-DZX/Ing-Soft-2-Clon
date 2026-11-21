from decimal import Decimal

from .ConversorMoneda import ConversorMoneda
from .Divisa import Divisa


class ConversorDolares(ConversorMoneda):
    codigo = Divisa.USD.value
    nombre = Divisa.USD.label
    simbolo = "$"

    def __init__(self, soles_por_dolar):
        self._soles_por_dolar = Decimal(str(soles_por_dolar))

    def soles_por_unidad(self):
        return self._soles_por_dolar

    def convertir(self, monto_en_soles):
        return (monto_en_soles / self._soles_por_dolar).quantize(Decimal("0.01"))
