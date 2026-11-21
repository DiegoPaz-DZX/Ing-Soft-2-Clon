from decimal import Decimal

from .ConversorMoneda import ConversorMoneda
from .Divisa import Divisa


class ConversorSoles(ConversorMoneda):
    codigo = Divisa.PEN.value
    nombre = Divisa.PEN.label
    simbolo = "S/"

    def soles_por_unidad(self):
        return Decimal("1")

    def convertir(self, monto_en_soles):
        return monto_en_soles
